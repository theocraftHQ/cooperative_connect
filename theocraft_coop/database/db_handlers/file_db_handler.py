import logging
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import joinedload

import theocraft_coop.schemas.file_schemas as schemas
from theocraft_coop.database.orms.misc_orm import File as File_DB
from theocraft_coop.root.database import async_session
from theocraft_coop.services.service_utils.exception_collection import (
    CreateError,
    NotFound,
)

LOGGER = logging.getLogger(__name__)


async def create_file(files: list[schemas.File]):
    async with async_session() as session:
        stmt = (
            insert(File_DB)
            .values([file.model_dump() for file in files])
            .returning(File_DB)
        )

        result = (await session.execute(statement=stmt)).scalars()

        if not result:
            LOGGER.error("create_file failed")
            await session.rollback()
            raise CreateError

        await session.commit()
        return [schemas.FileRead(**x.as_dict()) for x in result]


async def get(file_id: UUID):
    async with async_session() as session:
        result = (
            await session.execute(
                select(File_DB)
                .options(joinedload(File_DB.creator))
                .where(File_DB.id == file_id)
            )
        ).scalar_one_or_none()

        if not result:
            raise NotFound

        return schemas.FileRead(**result.as_dict(), creator=result.creator)


async def update_file(file_id: UUID, link: str):
    async with async_session() as session:
        result = (
            await session.execute(
                update(File_DB)
                .where(File_DB.id == file_id)
                .values(
                    link=link, link_expiration=datetime.now() + timedelta(seconds=72000)
                )
                .returning(File_DB)
            )
        ).scalar_one_or_none()

        if not result:
            await session.rollback()
            raise NotFound

        await session.commit()

        return schemas.FileRead(**result.as_dict(), creator=result.creator)


async def delete_file(file_id: UUID):
    async with async_session() as session:
        result = (
            await session.execute(
                delete(File_DB).where(File_DB.id == file_id).returning(File_DB)
            )
        ).scalar_one_or_none()

        if not result:
            await session.rollback()
            raise NotFound

        await session.commit()

        return schemas.FileRead(**result.as_dict(), creator=result.creator)
