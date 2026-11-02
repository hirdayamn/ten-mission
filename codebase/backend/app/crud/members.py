import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.members import Member
from app.schemas.members import MemberCreate, MemberUpdate
from app.crud.base import CRUDBase


class MemberCRUD(CRUDBase[Member, MemberCreate, MemberUpdate]):
    def __init__(self):
        super().__init__(Member)

    def _apply_search_filter(self, query, search_term: str):
        return query.where(
            or_(
                Member.full_name.ilike(f"%{search_term}%"),
                Member.first_name.ilike(f"%{search_term}%"),
                Member.last_name.ilike(f"%{search_term}%"),
            )
        )


member_crud = MemberCRUD()


# Backward compatibility functions
async def get_member(db: AsyncSession, member_id: uuid.UUID) -> Optional[Member]:
    return await member_crud.get(db, member_id)


async def get_members(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[Member]:
    items, _ = await member_crud.search(db, skip=skip, limit=limit)
    return items


async def get_member_for_update(db: AsyncSession, member_id: uuid.UUID) -> Optional[Member]:
    return await member_crud.get_for_update(db, member_id)


async def create_member(db: AsyncSession, member_in: MemberCreate) -> Member:
    return await member_crud.create(db, member_in)


async def update_member(
    db: AsyncSession,
    member_id: uuid.UUID,
    member_in: MemberUpdate,
) -> Optional[Member]:
    return await member_crud.update(db, member_id, member_in)


async def get_member_by_name_date(
    db: AsyncSession, first_name: str, last_name: str, joining_date: datetime
) -> Optional[Member]:
    result = await db.execute(
        select(Member).where(
            Member.first_name == first_name,
            Member.last_name == last_name,
            Member.joining_date == joining_date,
        )
    )
    return result.scalar_one_or_none()


async def upsert_member(db: AsyncSession, member_in: MemberCreate) -> Member:
    existing = await get_member_by_name_date(db, member_in.first_name, member_in.last_name, member_in.joining_date)
    if existing:
        update_data = member_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)
        await db.flush()
        await db.refresh(existing)
        return existing
    return await create_member(db, member_in)


async def search_members(
    db: AsyncSession,
    query: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Member], int]:
    return await member_crud.search(db, query, skip, limit)