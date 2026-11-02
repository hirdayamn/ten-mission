import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.auth import get_current_user
from app.services.inventory import InventoryService
from app.schemas import InventoryResponse, InventoryListResponse
from app.routers.utils import paginated_response, get_or_404

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=InventoryListResponse)
async def list_inventory(
    q: Optional[str] = Query(None, description="Search query for title or description"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = InventoryService(db)
    skip = (page - 1) * page_size
    items, total = await service.search(q, skip, page_size)

    return paginated_response(items, total, page, page_size, InventoryResponse)


@router.get("/{inventory_id}", response_model=InventoryResponse)
async def get_inventory(
    inventory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = InventoryService(db)
    item = await get_or_404(inventory_id, service.get)
    return item