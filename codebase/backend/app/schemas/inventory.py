import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class InventoryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    remaining_count: int = Field(..., ge=0)
    expiration_date: datetime
    is_active: bool = True


class InventoryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    remaining_count: Optional[int] = Field(None, ge=0)
    expiration_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class InventoryResponse(InventoryBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


# Type aliases for backward compatibility
InventoryCreate = InventoryBase