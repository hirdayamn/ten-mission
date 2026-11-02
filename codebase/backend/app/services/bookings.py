import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.bookings import Booking
from app.models.inventory import Inventory
from app.models.members import Member
from app.crud.bookings import (
    get_booking_by_reference,
    get_bookings_by_member,
    cancel_booking,
    get_active_bookings_count,
)
from app.crud.inventory import get_inventory_for_update, get_inventory
from app.crud.members import get_member_for_update, get_member
from app.core.config import settings
from app.core.exceptions import (
    MemberNotFoundError,
    InventoryNotFoundError,
    MaxBookingsExceededError,
    InsufficientInventoryError,
    BookingNotFoundError,
    InvalidBookingStateError,
    ExpiredInventoryError,
    InactiveInventoryError,
)


class BookingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def book_inventory(
        self,
        member_id: uuid.UUID,
        inventory_id: uuid.UUID,
        quantity: int = 1,
        created_by: str = "",
    ) -> Booking:
        # Don't use db.begin() here - the API layer manages the transaction
        member = await get_member_for_update(self.db, member_id)
        if not member:
            raise MemberNotFoundError()

        inventory = await get_inventory_for_update(self.db, inventory_id)
        if not inventory:
            raise InventoryNotFoundError()

        if not inventory.is_active:
            raise InactiveInventoryError()

        if inventory.expiration_date < datetime.now(timezone.utc):
            raise ExpiredInventoryError()

        active_count = await get_active_bookings_count(self.db, member_id)
        if active_count + quantity > settings.MAX_BOOKINGS:
            raise MaxBookingsExceededError(current_count=active_count, limit=settings.MAX_BOOKINGS)

        if inventory.remaining_count < quantity:
            raise InsufficientInventoryError(
                f"Insufficient inventory. Available: {inventory.remaining_count}"
            )

        inventory.remaining_count -= quantity

        booking = Booking(
            member_id=member_id,
            inventory_id=inventory_id,
            booking_date=datetime.now(timezone.utc),
            is_active=True,
            created_by=created_by,
        )
        self.db.add(booking)
        await self.db.flush()
        await self.db.refresh(booking)

        member.booking_count = active_count + quantity

        # Enrich with member name and inventory title
        member_record = await get_member(self.db, member_id)
        inventory_record = await get_inventory(self.db, inventory_id)
        booking.member_name = member_record.full_name if member_record else None
        booking.inventory_title = inventory_record.title if inventory_record else None

        return booking

    async def cancel_booking(self, booking_reference: str, cancelled_by: str) -> Optional[Booking]:
        booking = await get_booking_by_reference(self.db, booking_reference)
        if not booking:
            raise BookingNotFoundError()
        if not booking.is_active:
            raise InvalidBookingStateError("Booking is already cancelled")

        booking.is_active = False
        booking.cancelled_by = cancelled_by

        inventory = await get_inventory_for_update(self.db, booking.inventory_id)
        if inventory:
            inventory.remaining_count += 1

        member = await get_member_for_update(self.db, booking.member_id)
        if member:
            active_count = await get_active_bookings_count(self.db, member.id)
            member.booking_count = max(0, active_count - 1)

        # Enrich with member name and inventory title for response
        member_record = await get_member(self.db, booking.member_id)
        inventory_record = await get_inventory(self.db, booking.inventory_id)
        booking.member_name = member_record.full_name if member_record else None
        booking.inventory_title = inventory_record.title if inventory_record else None

        await self.db.flush()
        await self.db.refresh(booking)
        return booking

    async def get_booking(self, booking_reference: str) -> Optional[Booking]:
        return await get_booking_by_reference(self.db, booking_reference)

    async def get_member_bookings(
        self,
        member_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> list[tuple[Booking, str, str]]:
        return await get_bookings_by_member(self.db, member_id, skip, limit, active_only)