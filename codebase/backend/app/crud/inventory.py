import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inventory import Inventory
from app.models.bookings import Booking
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from app.crud.base import CRUDBase


class InventoryCRUD(CRUDBase[Inventory, InventoryCreate, InventoryUpdate]):
    def __init__(self):
        super().__init__(Inventory)

    def _apply_search_filter(self, query, search_term: str):
        return query.where(
            or_(
                Inventory.title.ilike(f"%{search_term}%"),
                Inventory.description.ilike(f"%{search_term}%"),
            )
        )

    async def search(
        self,
        db: AsyncSession,
        query: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Inventory], int]:
        base_query = select(Inventory)
        count_query = select(func.count(Inventory.id))

        if query:
            base_query = self._apply_search_filter(base_query, query)
            count_query = self._apply_search_filter(count_query, query)

        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        base_query = base_query.order_by(Inventory.is_active.desc(), Inventory.id).offset(skip).limit(limit)
        result = await db.execute(base_query)
        items = result.scalars().all()

        return items, total


inventory_crud = InventoryCRUD()


# Backward compatibility functions
async def get_inventory(db: AsyncSession, inventory_id: uuid.UUID) -> Optional[Inventory]:
    return await inventory_crud.get(db, inventory_id)


async def get_inventories(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[Inventory]:
    items, _ = await inventory_crud.search(db, skip=skip, limit=limit)
    return items


async def get_inventory_for_update(db: AsyncSession, inventory_id: uuid.UUID) -> Optional[Inventory]:
    return await inventory_crud.get_for_update(db, inventory_id)


async def create_inventory(db: AsyncSession, inventory_in: InventoryCreate) -> Inventory:
    return await inventory_crud.create(db, inventory_in)


async def update_inventory(
    db: AsyncSession,
    inventory_id: uuid.UUID,
    inventory_in: InventoryUpdate,
) -> Optional[Inventory]:
    return await inventory_crud.update(db, inventory_id, inventory_in)


async def get_inventory_by_title(db: AsyncSession, title: str) -> Optional[Inventory]:
    result = await db.execute(select(Inventory).where(Inventory.title == title))
    return result.scalar_one_or_none()


async def upsert_inventory(db: AsyncSession, inventory_in: InventoryCreate) -> Inventory:
    existing = await get_inventory_by_title(db, inventory_in.title)
    if existing:
        update_data = inventory_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)
        await db.flush()
        await db.refresh(existing)
        return existing
    return await create_inventory(db, inventory_in)


async def search_inventories(
    db: AsyncSession,
    query: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Inventory], int]:
    return await inventory_crud.search(db, query, skip, limit)


async def get_inventory_for_member(
    db: AsyncSession,
    member_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Inventory], int]:
    """
    Get available inventory for a specific member.
    Excludes items already actively booked by the member, out of stock, and inactive items.
    """
    now = datetime.now(timezone.utc)

    active_booking_join = and_(
        Booking.inventory_id == Inventory.id,
        Booking.member_id == member_id,
        Booking.is_active == True,
    )

    base_query = (
        select(Inventory)
        .outerjoin(Booking, active_booking_join)
        .where(Booking.id.is_(None))
        .where(Inventory.remaining_count > 0)
        .where(Inventory.is_active == True)
        .where(Inventory.expiration_date > now)
    )
    count_query = (
        select(func.count(Inventory.id))
        .outerjoin(Booking, active_booking_join)
        .where(
            Booking.id.is_(None),
            Inventory.remaining_count > 0,
            Inventory.is_active == True,
            Inventory.expiration_date > now,
        )
    )

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(
        base_query.order_by(Inventory.id).offset(skip).limit(limit)
    )
    items = result.scalars().all()

    return items, total