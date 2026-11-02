from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ListResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


from app.schemas.inventory import (
    InventoryBase,
    InventoryUpdate,
    InventoryResponse,
    InventoryCreate,
)
from app.schemas.members import (
    MemberBase,
    MemberUpdate,
    MemberResponse,
    MemberLogin,
    MemberCreate,
)
from app.schemas.bookings import (
    BookingCreate,
    BookingResponse,
    BookingCancelRequest,
)
from app.schemas.auth import (
    Token,
    TokenData,
)

# Type aliases for backward compatibility
InventoryListResponse = ListResponse["InventoryResponse"]
MemberListResponse = ListResponse["MemberResponse"]
BookingListResponse = ListResponse["BookingResponse"]

__all__ = [
    "ListResponse",
    "InventoryBase",
    "InventoryUpdate",
    "InventoryResponse",
    "InventoryListResponse",
    "InventoryCreate",
    "MemberBase",
    "MemberUpdate",
    "MemberResponse",
    "MemberListResponse",
    "MemberCreate",
    "MemberLogin",
    "BookingCreate",
    "BookingResponse",
    "BookingCancelRequest",
    "BookingListResponse",
    "Token",
    "TokenData",
]