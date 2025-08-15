import logging
from uuid import UUID, uuid4

from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

import theocraft_coop.schemas.user_schemas as schemas
from theocraft_coop.database.orms.misc_orm import File
from theocraft_coop.database.orms.user_orm import MfaToken as MfaToken_DB
from theocraft_coop.database.orms.user_orm import User as User_DB
from theocraft_coop.database.orms.user_orm import UserBio as UserBio_DB
from theocraft_coop.root.database import async_session
from theocraft_coop.services.service_utils.exception_collection import (
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
        return schemas.UserProfile(**result.as_dict())


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

        return schemas.UserProfile(**result.as_dict())


async def get(user_id: UUID):
    async with async_session() as session:
        result = (
            (
                await session.execute(
                    select(User_DB)
                    .options(
                        joinedload(User_DB.bio).joinedload(
                            UserBio_DB.identification_file
                        ),
                        joinedload(User_DB.bio).joinedload(UserBio_DB.passport_file),
                        joinedload(User_DB.bio).joinedload(UserBio_DB.signature_file),
                    )
                    .where(User_DB.id == user_id)
                )
            )
            .unique()
            .scalar_one_or_none()
        )

        if not result:
            raise NotFound

        return schemas.UserProfile(**result.as_dict(), bio=result.bio)


async def update_user(user_update: schemas.UserUpdate, user_id: UUID):

    async with async_session() as session:
        stmt = (
            update(User_DB)
            .where(User_DB.id == user_id)
            .values(
                user_update.model_dump(
                    exclude_none=True, exclude_unset=True, exclude={"user_bio"}
                )
            )
            .returning(User_DB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            raise UpdateError

        await session.commit()
        return schemas.UserProfile(**result.as_dict())


async def delete_user(): ...


async def create_mfa_token(
    code: str,
    phone_number: schemas.PhoneNumber = None,
    email: schemas.EmailStr = None,
):
    async with async_session() as session:

        stmt = (
            insert(MfaToken_DB)
            .values(phone_number=phone_number, email=email, code=code)
            .returning(MfaToken_DB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            await session.rollback()
            raise CreateError

        await session.commit()

        return result


async def get_mfa_token(code: str):
    async with async_session() as session:

        stmt = select(MfaToken_DB).filter(MfaToken_DB.code == code)

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            raise NotFound

        return result


async def get_mfa_token_via_user_info(phone_number: str = None, email: str = None):
    filter_array = []
    if phone_number is None:
        filter_array.append(MfaToken_DB.phone_number == phone_number)
    if email is None:
        filter_array.append(MfaToken_DB.email == email)

    async with async_session() as session:

        stmt = select(MfaToken_DB).filter(
            and_(*filter_array, MfaToken_DB.verified == False)  # noqa: E712
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            raise NotFound

        return result


async def update_mfa_token(id: UUID, verified: bool = False):

    async with async_session() as session:
        stmt = (
            update(MfaToken_DB)
            .filter(MfaToken_DB.id == id)
            .values(
                code=f"XXYYZZ-{uuid4()}",
                verified=verified,
            )
            .returning(MfaToken_DB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            await session.rollback()

        await session.commit()

        return result


async def delete_mfa_token(id: UUID):

    async with async_session() as session:
        stmt = delete(MfaToken_DB).filter(MfaToken_DB.id == id).returning(MfaToken_DB)

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            await session.rollback()

        await session.commit()

        return result


async def create_user_bio(user_bio: schemas.UserBio, user_id: UUID):
    async with async_session() as session:
        stmt = (
            insert(UserBio_DB)
            .values(
                **user_bio.model_dump(exclude_none=True, exclude_unset=True),
                user_id=user_id,
            )
            .returning(UserBio_DB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            await session.rollback()
            raise CreateError(
                f"User Bio creation failed. Please check the input data: {user_bio.model_dump()}"
            )

        await session.commit()
        return schemas.UserBio(**result.as_dict())


async def get_user_bio(user_id: UUID):
    async with async_session() as session:
        stmt = select(UserBio_DB).filter(UserBio_DB.user_id == user_id)

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            raise NotFound(f"User Bio not found for user_id: {user_id}")

        return schemas.UserBio(**result.as_dict())


async def update_user_bio(user_bio: schemas.UserBio, user_id: UUID):
    async with async_session() as session:
        stmt = (
            update(UserBio_DB)
            .filter(UserBio_DB.user_id == user_id)
            .values(**user_bio.model_dump(exclude_none=True, exclude_unset=True))
            .returning(UserBio_DB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            await session.rollback()
            raise UpdateError(f"User Bio update failed for user_id: {user_id}")

        await session.commit()
        return schemas.UserBio(**result.as_dict())
