import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.bookings import Booking
from app.models.inventory import Inventory
from app.models.members import Member
from app.schemas.bookings import BookingCreate


async def create_booking(db: AsyncSession, booking_in: BookingCreate, created_by: str) -> Booking:
    booking = Booking(
        member_id=booking_in.member_id,
        inventory_id=booking_in.inventory_id,
        booking_date=datetime.now(timezone.utc),
        is_active=True,
        created_by=created_by,
    )
    db.add(booking)
    await db.flush()
    await db.refresh(booking)
    return booking


async def get_booking_by_reference(db: AsyncSession, booking_reference: str) -> Optional[Booking]:
    result = await db.execute(
        select(Booking).where(Booking.booking_reference == booking_reference)
    )
    return result.scalar_one_or_none()


async def get_bookings_by_member(
    db: AsyncSession,
    member_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
) -> list[tuple[Booking, str, str]]:
    query = (
        select(Booking, Member.full_name, Inventory.title)
        .join(Member, Booking.member_id == Member.id)
        .join(Inventory, Booking.inventory_id == Inventory.id)
        .where(Booking.member_id == member_id)
    )
    if active_only:
        query = query.where(Booking.is_active == True)
    query = query.order_by(Booking.booking_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.all()


async def get_active_bookings_count(db: AsyncSession, member_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count(Booking.id)).where(
            and_(Booking.member_id == member_id, Booking.is_active == True)
        )
    )
    return result.scalar_one()


async def cancel_booking(db: AsyncSession, booking_reference: str, cancelled_by: str) -> Optional[Booking]:
    booking = await get_booking_by_reference(db, booking_reference)
    if not booking or not booking.is_active:
        return None
    booking.is_active = False
    booking.cancelled_by = cancelled_by
    await db.flush()
    await db.refresh(booking)
    return booking


async def search_bookings(
    db: AsyncSession,
    member_id: Optional[uuid.UUID] = None,
    active_only: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[tuple[Booking, str, str]], int]:
    base_query = (
        select(Booking, Member.full_name, Inventory.title)
        .join(Member, Booking.member_id == Member.id)
        .join(Inventory, Booking.inventory_id == Inventory.id)
    )
    count_query = select(func.count(Booking.id))

    if member_id:
        base_query = base_query.where(Booking.member_id == member_id)
        count_query = count_query.where(Booking.member_id == member_id)

    if active_only:
        base_query = base_query.where(Booking.is_active == True)
        count_query = count_query.where(Booking.is_active == True)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    base_query = base_query.order_by(Booking.booking_date.desc()).offset(skip).limit(limit)
    result = await db.execute(base_query)
    items = result.all()

    return items, total