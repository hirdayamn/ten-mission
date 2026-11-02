import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class MemberBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)
    booking_count: int = Field(default=0, ge=0)
    joining_date: datetime


class MemberUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    booking_count: Optional[int] = Field(None, ge=0)
    joining_date: Optional[datetime] = None


class MemberResponse(MemberBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class MemberLogin(BaseModel):
    email: EmailStr


# Type aliases for backward compatibility
MemberCreate = MemberBase