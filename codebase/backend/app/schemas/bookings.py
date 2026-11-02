import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class BookingCreate(BaseModel):
    member_id: uuid.UUID
    inventory_id: uuid.UUID
    quantity: int = Field(default=1, gt=0, le=1)


class BookingResponse(BaseModel):
    id: uuid.UUID
    member_id: uuid.UUID
    inventory_id: uuid.UUID
    member_name: Optional[str] = None
    inventory_title: Optional[str] = None
    booking_date: datetime
    is_active: bool
    booking_reference: str
    created_by: str
    cancelled_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BookingCancelRequest(BaseModel):
    booking_reference: str = Field(..., min_length=36, max_length=36)