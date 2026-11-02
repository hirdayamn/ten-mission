import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.inventory import (
    get_inventory,
    get_inventory_for_update,
    create_inventory,
    update_inventory,
    search_inventories,
    get_inventory_for_member,
)
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from app.services.base import BaseService


class InventoryService(BaseService):
    crud_get = staticmethod(get_inventory)
    crud_get_for_update = staticmethod(get_inventory_for_update)
    crud_search = staticmethod(search_inventories)
    crud_create = staticmethod(create_inventory)
    crud_update = staticmethod(update_inventory)

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_for_member(
        self,
        member_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ):
        return await get_inventory_for_member(self.db, member_id, skip, limit)