import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.members import (
    get_member,
    get_member_for_update,
    create_member,
    update_member,
    search_members,
)
from app.schemas.members import MemberCreate, MemberUpdate
from app.services.base import BaseService


class MemberService(BaseService):
    crud_get = staticmethod(get_member)
    crud_get_for_update = staticmethod(get_member_for_update)
    crud_search = staticmethod(search_members)
    crud_create = staticmethod(create_member)
    crud_update = staticmethod(update_member)

    def __init__(self, db: AsyncSession):
        super().__init__(db)