import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.auth import get_current_user
from app.services.members import MemberService
from app.services.inventory import InventoryService
from app.schemas import MemberResponse, MemberListResponse, InventoryResponse, InventoryListResponse
from app.routers.utils import paginated_response, get_or_404

router = APIRouter(prefix="/members", tags=["members"])


@router.get("", response_model=MemberListResponse)
async def list_members(
    q: Optional[str] = Query(None, description="Search query for member name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = MemberService(db)
    skip = (page - 1) * page_size
    items, total = await service.search(q, skip, page_size)
    return paginated_response(items, total, page, page_size, MemberResponse)


@router.get("/{member_id}", response_model=MemberResponse)
async def get_member(
    member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = MemberService(db)
    item = await get_or_404(member_id, service.get)
    return item


@router.get("/{member_id}/available-inventory", response_model=InventoryListResponse)
async def list_available_inventory_for_member(
    member_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Verify member exists
    member_service = MemberService(db)
    member = await get_or_404(member_id, member_service.get)

    inventory_service = InventoryService(db)
    skip = (page - 1) * page_size
    items, total = await inventory_service.get_for_member(member_id, skip, page_size)
    return paginated_response(items, total, page, page_size, InventoryResponse)