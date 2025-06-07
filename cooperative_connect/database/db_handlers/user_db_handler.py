import logging
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError

import cooperative_connect.schemas.user_schemas as schemas
from cooperative_connect.database.orms.user_orm import User as User_DB
from cooperative_connect.root.database import async_session
from cooperative_connect.services.service_utils.exception_collection import (
    CreateError,
    DuplicateError,
    NotFound,
    UpdateError,
)

LOGGER = logging.getLogger(__name__)


async def create_user(user: schemas.User):
    async with async_session() as session:
        stmt = insert(User_DB).values(user.model_dump()).returning(User_DB)
        try:
            result = (await session.execute(statement=stmt)).scalar_one_or_none()
        except IntegrityError as e:
            LOGGER.error(f"duplicate record found for {user.model_dump()}")
            await session.rollback()
            raise DuplicateError
        if not result:
            LOGGER.error("create_admin failed")
            await session.rollback()
            raise CreateError

        await session.commit()
        return result


async def get_user(email: str = None, phone_number: str = None):
    filter_array = []
    if email:
        filter_array.append(User_DB.email == email)
    if phone_number:
        filter_array.append(User_DB.phone_number == phone_number)

    async with async_session() as session:
        result = (
            await session.execute(select(User_DB).where(*filter_array))
        ).scalar_one_or_none()

        if not result:
            raise NotFound

        return result


async def get(user_id: UUID):
    async with async_session() as session:
        result = (
            await session.execute(select(User_DB).where(User_DB.id == user_id))
        ).scalar_one_or_none()

        if not result:
            raise NotFound

        return result


async def update_user(user_update: schemas.UserUpdate, user_id: UUID):

    async with async_session() as session:
        stmt = (
            update(User_DB)
            .where(User_DB.id == user_id)
            .values(user_update.model_dump(exclude_none=True, exclude_unset=True))
            .returning(User_DB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            raise UpdateError

        await session.commit()
        return result


async def delete_user(): ...
