import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.auth import get_current_user
from app.services.bookings import BookingService
from app.schemas import BookingCreate, BookingResponse, BookingCancelRequest, BookingListResponse
from app.crud.bookings import search_bookings

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/book", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def book_inventory(
    booking_in: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = BookingService(db)
    try:
        booking = await service.book_inventory(
            member_id=booking_in.member_id,
            inventory_id=booking_in.inventory_id,
            quantity=booking_in.quantity,
            created_by=current_user["sub"],
        )
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cancel", response_model=BookingResponse)
async def cancel_booking(
    cancel_in: BookingCancelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = BookingService(db)
    booking = await service.cancel_booking(cancel_in.booking_reference, cancelled_by=current_user["sub"])
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or already cancelled")
    return booking


@router.get("", response_model=BookingListResponse)
async def list_bookings(
    member_id: uuid.UUID = Query(..., description="Member ID to filter bookings"),
    active_only: bool = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    skip = (page - 1) * page_size

    rows, total = await search_bookings(
        db, member_id=member_id, active_only=active_only, skip=skip, limit=page_size
    )
    items = [
        BookingResponse(
            id=booking.id,
            member_id=booking.member_id,
            inventory_id=booking.inventory_id,
            member_name=member_name,
            inventory_title=inventory_title,
            booking_date=booking.booking_date,
            is_active=booking.is_active,
            booking_reference=booking.booking_reference,
            created_by=booking.created_by,
            cancelled_by=booking.cancelled_by,
        )
        for booking, member_name, inventory_title in rows
    ]

    return BookingListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )