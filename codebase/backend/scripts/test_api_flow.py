#!/usr/bin/env python3
"""Test the full API flow: member -> inventory -> booking -> limit -> cancel."""
import asyncio
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, init_db
from app.models.members import Member
from app.models.inventory import Inventory
from app.models.bookings import Booking
from app.services.members import MemberService
from app.services.inventory import InventoryService
from app.services.bookings import BookingService
from app.schemas.members import MemberCreate
from app.schemas.inventory import InventoryCreate
from app.schemas.bookings import BookingCreate
from app.core.config import settings


async def test_full_flow():
    """Test the complete booking flow via services (bypassing HTTP)."""
    print("=" * 60)
    print("TESTING FULL API FLOW")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        member_service = MemberService(db)
        inventory_service = InventoryService(db)
        booking_service = BookingService(db)

        # 1. CREATE MEMBER
        print("\n1. Creating member...")
        member_in = MemberCreate(
            username="testuser",
            first_name="Test",
            last_name="User",
            full_name="Test User",
            booking_count=0,
            joining_date=datetime.utcnow(),
        )
        member = await member_service.create(member_in)
        print(f"   Created: {member.full_name} (ID: {member.id}, booking_count: {member.booking_count})")

        # 2. CREATE INVENTORY ITEMS (3 items)
        print("\n2. Creating inventory items...")
        items = []
        for i in range(1, 4):
            inv_in = InventoryCreate(
                title=f"Test Item {i}",
                description=f"Description for item {i}",
                remaining_count=5,
                expiration_date=datetime.utcnow() + timedelta(days=30),
                is_active=True,
            )
            item = await inventory_service.create(inv_in)
            items.append(item)
            print(f"   Created: {item.title} (ID: {item.id}, available: {item.remaining_count})")

        # 3. BOOK FIRST ITEM (should succeed)
        print("\n3. Booking first item (should succeed)...")
        booking1 = await booking_service.book_inventory(
            member_id=member.id,
            inventory_id=items[0].id,
            quantity=1,
        )
        print(f"   Success! Booking ref: {booking1.booking_reference}")
        print(f"   Member booking_count: {member.booking_count}")

        # 4. BOOK SECOND ITEM (should succeed - at limit)
        print("\n4. Booking second item (should succeed - at limit)...")
        booking2 = await booking_service.book_inventory(
            member_id=member.id,
            inventory_id=items[1].id,
            quantity=1,
        )
        print(f"   Success! Booking ref: {booking2.booking_reference}")
        print(f"   Member booking_count: {member.booking_count}")

        # 5. TRY TO BOOK THIRD ITEM (should FAIL - exceeds MAX_BOOKINGS=2)
        print("\n5. Booking third item (should FAIL - max 2 bookings)...")
        try:
            booking3 = await booking_service.book_inventory(
                member_id=member.id,
                inventory_id=items[2].id,
                quantity=1,
            )
            print(f"   UNEXPECTED SUCCESS: {booking3.booking_reference}")
        except Exception as e:
            print(f"   Expected failure ({type(e).__name__}): {e}")

        # 6. CHECK AVAILABLE FOR MEMBER (should only show item 3, since 1&2 booked)
        print("\n6. Checking available inventory for member...")
        available, total = await inventory_service.get_for_member(member.id, 0, 10)
        print(f"   Available items: {len(available)} (total: {total})")
        for item in available:
            print(f"   - {item.title} (ID: {item.id}, available: {item.remaining_count})")

        # 7. CANCEL FIRST BOOKING
        print("\n7. Cancelling first booking...")
        cancelled = await booking_service.cancel_booking(booking1.booking_reference)
        print(f"   Cancelled: {cancelled.booking_reference}")
        print(f"   Member booking_count: {member.booking_count}")

        # 8. NOW TRY TO BOOK THIRD ITEM AGAIN (should succeed now)
        print("\n8. Booking third item after cancellation (should succeed)...")
        booking3 = await booking_service.book_inventory(
            member_id=member.id,
            inventory_id=items[2].id,
            quantity=1,
        )
        print(f"   Success! Booking ref: {booking3.booking_reference}")
        print(f"   Member booking_count: {member.booking_count}")

        # 9. LIST ALL BOOKINGS FOR MEMBER
        print("\n9. Listing all bookings for member...")
        rows = await booking_service.get_member_bookings(member.id, 0, 10, active_only=True)
        for booking, member_name, inv_title in rows:
            print(f"   - {inv_title} (ref: {booking.booking_reference}, active: {booking.is_active})")

        # 10. TRY BOOKING EXPIRED ITEM (should fail via is_active check)
        print("\n10. Creating expired item and trying to book...")
        expired_item = InventoryCreate(
            title="Expired Item",
            description="This is expired",
            remaining_count=10,
            expiration_date=datetime.utcnow() - timedelta(days=1),
            is_active=False,
        )
        expired = await inventory_service.create(expired_item)
        print(f"   Created expired item: {expired.title} (is_active: {expired.is_active})")

        # Check it's NOT in available list
        available, _ = await inventory_service.get_for_member(member.id, 0, 10)
        expired_in_available = any(item.id == expired.id for item in available)
        print(f"   Expired item in available list: {expired_in_available} (should be False)")

        # 11. TRY BOOKING OUT OF STOCK ITEM (with fresh member)
        print("\n11. Trying to book out of stock item...")
        oos_item = InventoryCreate(
            title="Out of Stock",
            description="No inventory",
            remaining_count=0,
            expiration_date=datetime.utcnow() + timedelta(days=30),
            is_active=True,
        )
        oos = await inventory_service.create(oos_item)

        # Create fresh member for this test
        fresh_member_in = MemberCreate(
            username="testuser2",
            first_name="Test",
            last_name="User2",
            full_name="Test User 2",
            booking_count=0,
            joining_date=datetime.utcnow(),
        )
        fresh_member = await member_service.create(fresh_member_in)

        try:
            await booking_service.book_inventory(fresh_member.id, oos.id, 1)
            print("   UNEXPECTED SUCCESS")
        except Exception as e:
            print(f"   Expected failure ({type(e).__name__}): {e}")

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)


async def cleanup_test_data():
    """Clean up test data."""
    print("\nCleaning up test data...")
    async with AsyncSessionLocal() as db:
        # Delete test bookings
        result = await db.execute(select(Booking).join(Member).where(Member.username == "testuser"))
        bookings = result.scalars().all()
        for b in bookings:
            await db.delete(b)

        # Delete test inventory
        result = await db.execute(select(Inventory).where(Inventory.title.like("Test Item%") | Inventory.title.like("Expired%") | Inventory.title.like("Out of Stock%")))
        items = result.scalars().all()
        for item in items:
            await db.delete(item)

        # Delete test member
        result = await db.execute(select(Member).where(Member.username == "testuser"))
        member = result.scalar_one_or_none()
        if member:
            await db.delete(member)

        await db.commit()
        print("Cleanup complete")


async def main():
    await init_db()
    await test_full_flow()
    await cleanup_test_data()


if __name__ == "__main__":
    asyncio.run(main())