from typing import Generic, Optional, TypeVar, Any
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic base CRUD class providing standard operations.
    Subclasses define the model and implement entity-specific queries.
    """

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_for_update(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        result = await db.execute(
            select(self.model).where(self.model.id == id).with_for_update()
        )
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj = self.model(**obj_in.model_dump())
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def update(
        self,
        db: AsyncSession,
        id: UUID,
        obj_in: UpdateSchemaType,
    ) -> Optional[ModelType]:
        obj = await self.get(db, id)
        if not obj:
            return None
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(obj, field, value)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def search(
        self,
        db: AsyncSession,
        query: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ModelType], int]:
        base_query = select(self.model)
        count_query = select(func.count(self.model.id))

        if query:
            base_query = self._apply_search_filter(base_query, query)
            count_query = self._apply_search_filter(count_query, query)

        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        base_query = base_query.order_by(self.model.id).offset(skip).limit(limit)
        result = await db.execute(base_query)
        items = result.scalars().all()

        return items, total

    def _apply_search_filter(self, query, search_term: str):
        """Override in subclass to implement entity-specific search."""
        raise NotImplementedError("Subclass must implement _apply_search_filter")