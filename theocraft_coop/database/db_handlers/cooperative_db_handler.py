import logging
from uuid import UUID, uuid4

from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from theocraft_coop.database.orms.cooperative_orm import Cooperative as Cooperative_DB
from theocraft_coop.database.orms.cooperative_orm import CooperativeUser as CooperativeUser_DB
from theocraft_coop.database.orms.cooperative_orm import Member as Member_DB


from theocraft_coop.root.database import async_session
from theocraft_coop.services.service_utils.exception_collection import (
    CreateError,
    DuplicateError,
    NotFound,
    UpdateError,
)

LOGGER = logging.getLogger(__name__)

async def get_coop(db_coop_id: UUID):
    async with async_session() as session:
        result = (
            await session.execute(select(Cooperative_DB).where(id=db_coop_id))
        ).scalar_one_or_none()

        if not result:
            raise NotFound

        return result
    
async def get_coop_user(coop_user_id: UUID, db_coop_id: UUID= None):
    # filter_array = []
    async with async_session() as session:
        result = (
            await session.execute(select(CooperativeUser_DB).where(id=coop_user_id))
        ).scalar_one_or_none()

        if not result:
            raise NotFound

        return result

async def get_coop_member(db_member_id: UUID, db_coop_id: UUID= None):
    # filter_array = []
    async with async_session() as session:
        result = (
            await session.execute(select(Member_DB).where(id=db_member_id))
        ).scalar_one_or_none()

        if not result:
            raise NotFound

        return result