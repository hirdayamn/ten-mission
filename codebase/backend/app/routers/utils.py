from typing import Callable, Generic, TypeVar
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db


T = TypeVar("T")
ResponseModel = TypeVar("ResponseModel")


def paginated_response(
    items: list[T],
    total: int,
    page: int,
    page_size: int,
    response_model: type[ResponseModel],
) -> "ListResponse[ResponseModel]":
    """Create a paginated list response."""
    from app.schemas import ListResponse
    return ListResponse[response_model](
        items=[response_model.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


async def get_or_404(
    id: UUID,
    getter_fn: Callable[[UUID], any],
) -> any:
    """Get an item by ID or raise 404."""
    item = await getter_fn(id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return item