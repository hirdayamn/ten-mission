from typing import Generic, Optional, TypeVar
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic base service providing standard CRUD operations.
    Subclasses should define the CRUD functions as class attributes.
    """

    # CRUD function references - to be defined by subclasses
    crud_get: Optional[callable] = None
    crud_get_for_update: Optional[callable] = None
    crud_search: Optional[callable] = None
    crud_create: Optional[callable] = None
    crud_update: Optional[callable] = None

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: UUID) -> Optional[ModelType]:
        if self.crud_get is None:
            raise NotImplementedError("crud_get must be defined in subclass")
        return await self.crud_get(self.db, id)

    async def get_for_update(self, id: UUID) -> Optional[ModelType]:
        if self.crud_get_for_update is None:
            raise NotImplementedError("crud_get_for_update must be defined in subclass")
        return await self.crud_get_for_update(self.db, id)

    async def search(
        self,
        query: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ):
        if self.crud_search is None:
            raise NotImplementedError("crud_search must be defined in subclass")
        return await self.crud_search(self.db, query, skip, limit)

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        if self.crud_create is None:
            raise NotImplementedError("crud_create must be defined in subclass")
        return await self.crud_create(self.db, obj_in)

    async def update(self, id: UUID, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        if self.crud_update is None:
            raise NotImplementedError("crud_update must be defined in subclass")
        return await self.crud_update(self.db, id, obj_in)