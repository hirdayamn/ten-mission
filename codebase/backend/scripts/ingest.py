import csv
import os
import re
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select, tuple_, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.members import Member
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryCreate
from app.schemas.members import MemberCreate


def to_title_case(text: str) -> str:
    """Convert text to Title Case: 'hello world' -> 'Hello World'"""
    words = re.split(r'[\s\-_]+', text.strip())
    return " ".join(w.capitalize() for w in words)


def sanitize_username(first_name: str, last_name: str) -> str:
    clean_first = re.sub(r'[^a-z0-9]', '', first_name.lower())
    clean_last = re.sub(r'[^a-z0-9]', '', last_name.lower())
    return f"{clean_first}_{clean_last}"


async def ingest_inventory(db: AsyncSession, fail_fast: bool = False) -> dict[str, Any]:
    """Ingest inventory from CSV using native PostgreSQL upsert."""
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "inventory.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    items: list[InventoryCreate] = []
    errors: list[dict] = []

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no headers")

        required_columns = ["title", "expiration_date", "remaining_count"]
        missing = [col for col in required_columns if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        for row_num, row in enumerate(reader, start=2):
            try:
                # Validate required fields
                for col in required_columns:
                    if col not in row or row[col] is None or row[col].strip() == "":
                        raise ValueError(f"Required field '{col}' is empty")

                # Parse expiration_date
                exp_date_str = row["expiration_date"].strip()
                try:
                    expiration_date = datetime.strptime(exp_date_str, "%d/%m/%Y").replace(tzinfo=timezone.utc)
                except ValueError:
                    try:
                        expiration_date = datetime.strptime(exp_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    except ValueError:
                        raise ValueError(f"Invalid date format: '{exp_date_str}'. Use DD/MM/YYYY or YYYY-MM-DD")

                # Parse remaining_count
                try:
                    remaining_count = int(row["remaining_count"])
                    if remaining_count < 0:
                        raise ValueError("Must be >= 0")
                except ValueError:
                    raise ValueError("Must be an integer")

                is_active = expiration_date > datetime.now(timezone.utc) and remaining_count > 0

                items.append(InventoryCreate(
                    title=to_title_case(row["title"]),
                    description=row["description"].strip() if row["description"] else None,
                    remaining_count=remaining_count,
                    expiration_date=expiration_date,
                    is_active=is_active,
                ))

            except ValueError as e:
                errors.append({"row": row_num, "field": "validation", "error": str(e)})
                if fail_fast:
                    break
            except Exception as e:
                errors.append({"row": row_num, "field": "unknown", "error": str(e)})
                if fail_fast:
                    break

    # Deduplicate within CSV by unique key (keep last occurrence)
    seen: dict[tuple[str, datetime], InventoryCreate] = {}
    for item in items:
        seen[(item.title, item.expiration_date)] = item
    items = list(seen.values())

    # Process valid items even if some rows had errors
    created = updated = 0
    if items:
        batch_size = 500
        for i in range(0, len(items), batch_size):
            chunk = items[i:i + batch_size]
            stmt = insert(Inventory).values([item.model_dump() for item in chunk])
            stmt = stmt.on_conflict_do_update(
                index_elements=["title", "expiration_date"],
                set_={
                    "description": stmt.excluded.description,
                    "remaining_count": stmt.excluded.remaining_count,
                    "is_active": stmt.excluded.is_active,
                }
            )
            result = await db.execute(stmt)
            created += result.rowcount if hasattr(result, 'rowcount') else len(chunk)

    return {"created": created, "updated": updated, "errors": len(errors), "error_details": errors}


async def ingest_members(db: AsyncSession, fail_fast: bool = False) -> dict[str, Any]:
    """Ingest members from CSV using native PostgreSQL upsert with unique username generation."""
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "members.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    items: list[MemberCreate] = []
    errors: list[dict] = []
    base_usernames: set[str] = set()

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no headers")

        required_columns = ["name", "surname", "date_joined"]
        missing = [col for col in required_columns if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        for row_num, row in enumerate(reader, start=2):
            try:
                first_name = row["name"].strip()
                if not first_name:
                    raise ValueError("First name cannot be empty")

                last_name = row["surname"].strip()
                if not last_name:
                    raise ValueError("Last name cannot be empty")

                full_name = f"{first_name} {last_name}"

                join_date_str = row["date_joined"].strip()
                try:
                    joining_date = datetime.fromisoformat(join_date_str.replace("Z", "+00:00"))
                except ValueError:
                    try:
                        joining_date = datetime.strptime(join_date_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
                    except ValueError:
                        raise ValueError(f"Invalid date format: '{join_date_str}'. Use ISO format or YYYY-MM-DDTHH:MM:SS")

                base_username = sanitize_username(first_name, last_name)
                base_usernames.add(base_username)

                items.append(MemberCreate(
                    username=base_username,  # placeholder
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    booking_count=0,
                    joining_date=joining_date,
                ))

            except ValueError as e:
                errors.append({"row": row_num, "field": "validation", "error": str(e)})
                if fail_fast:
                    break
            except Exception as e:
                errors.append({"row": row_num, "field": "unknown", "error": str(e)})
                if fail_fast:
                    break

    # Pre-fetch existing usernames for all bases in ONE query
    existing_usernames_map: dict[str, set[str]] = {}
    if base_usernames:
        patterns = [f"{base}%" for base in base_usernames]
        like_conditions = or_(*[Member.username.like(p) for p in patterns])
        result = await db.execute(select(Member.username).where(like_conditions))
        existing_usernames = {row[0] for row in result.all()}

        # Group by base username
        for base in base_usernames:
            pattern = re.compile(rf"^{re.escape(base)}(\d+)$")
            suffixes = set()
            for uname in existing_usernames:
                match = pattern.match(uname)
                if match:
                    suffixes.add(int(match.group(1)))
            existing_usernames_map[base] = suffixes

    # Fetch existing members by composite key (first_name, last_name, joining_date)
    keys = [(item.first_name, item.last_name, item.joining_date) for item in items]
    existing_map: dict[tuple, Member] = {}
    if keys:
        result = await db.execute(
            select(Member).where(tuple_(Member.first_name, Member.last_name, Member.joining_date).in_(keys))
        )
        existing_map = {(m.first_name, m.last_name, m.joining_date): m for m in result.scalars()}

    # Deduplicate within CSV by composite key (keep last occurrence)
    seen: dict[tuple, MemberCreate] = {}
    for item in items:
        key = (item.first_name, item.last_name, item.joining_date)
        seen[key] = item
    items = list(seen.values())

    # Assign unique usernames and split create/update
    to_create: list[MemberCreate] = []
    to_update: list[tuple[Member, MemberCreate]] = []
    local_counters: dict[str, int] = {base: max(suffixes) if suffixes else 0 for base, suffixes in existing_usernames_map.items()}

    for item in items:
        key = (item.first_name, item.last_name, item.joining_date)
        base = sanitize_username(item.first_name, item.last_name)

        if key in existing_map:
            # Keep existing username
            item.username = existing_map[key].username
            to_update.append((existing_map[key], item))
        else:
            count = local_counters[base]
            item.username = base if count == 0 else f"{base}{count}"
            local_counters[base] = count + 1
            to_create.append(item)

    created = updated = 0
    if to_create:
        batch_size = 500
        for i in range(0, len(to_create), batch_size):
            chunk = to_create[i:i + batch_size]
            stmt = insert(Member).values([item.model_dump() for item in chunk])
            # Username is unique - use ON CONFLICT DO NOTHING (shouldn't happen with our logic)
            stmt = stmt.on_conflict_do_nothing(index_elements=["username"])
            result = await db.execute(stmt)
            created += result.rowcount if hasattr(result, 'rowcount') else len(chunk)

    if to_update:
        for existing, item in to_update:
            for k, v in item.model_dump(exclude_unset=True, exclude={"username"}).items():
                setattr(existing, k, v)
        updated = len(to_update)

    await db.flush()
    return {"created": created, "updated": updated, "errors": len(errors), "error_details": errors}


async def main(fail_fast: bool = False):
    print("Starting data ingestion...")
    async with AsyncSessionLocal() as db:
        # Ingest inventory
        print("Running handler: inventory")
        inv_stats = await ingest_inventory(db, fail_fast=fail_fast)
        print(f"  Created: {inv_stats['created']}, Updated: {inv_stats['updated']}, Errors: {inv_stats['errors']}")
        if inv_stats["error_details"]:
            print(f"  Validation Errors ({len(inv_stats['error_details'])}):")
            for err in inv_stats["error_details"]:
                print(f"    Row {err['row']}, Field '{err['field']}': {err['error']}")

        # Ingest members
        print("Running handler: members")
        mem_stats = await ingest_members(db, fail_fast=fail_fast)
        print(f"  Created: {mem_stats['created']}, Updated: {mem_stats['updated']}, Errors: {mem_stats['errors']}")
        if mem_stats["error_details"]:
            print(f"  Validation Errors ({len(mem_stats['error_details'])}):")
            for err in mem_stats["error_details"]:
                print(f"    Row {err['row']}, Field '{err['field']}': {err['error']}")

        await db.commit()

    print("\n=== Ingestion Summary ===")
    print(f"\ninventory:")
    print(f"  Created: {inv_stats['created']}")
    print(f"  Updated: {inv_stats['updated']}")
    print(f"  Errors:  {inv_stats['errors']}")
    print(f"\nmembers:")
    print(f"  Created: {mem_stats['created']}")
    print(f"  Updated: {mem_stats['updated']}")
    print(f"  Errors:  {mem_stats['errors']}")


if __name__ == "__main__":
    import asyncio
    import sys
    fail_fast = "--fail-fast" in sys.argv
    asyncio.run(main(fail_fast=fail_fast))