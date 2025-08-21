import logging
from uuid import UUID, uuid4

from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from theocraft_coop.database.orms.cooperative_orm import Cooperative as Cooperative_DB
from theocraft_coop.database.orms.cooperative_orm import CooperativeUser as CooperativeUser_DB
from theocraft_coop.database.orms.cooperative_orm import Member as Member_DB


from theocraft_coop.root.database import async_session
import theocraft_coop.schemas.cooperative_schemas as schemas
from theocraft_coop.services.service_utils.exception_collection import (
    CreateError,
    DuplicateError,
    NotFound,
    UpdateError,
)

LOGGER = logging.getLogger(__name__)

async def create_coop_user(user_details: schemas.CooperativeUser, role: schemas.CooperativeUserRole = schemas.CooperativeUserRole.PRESIDENT):
    async with async_session() as session:
        stmt = insert(CooperativeUser_DB).values(**user_details.model_dump(), role=role).returning(CooperativeUser_DB)
        try:
            result = (await session.execute(statement=stmt)).scalar_one_or_none()
        except IntegrityError as e:
            LOGGER.error(f"duplicate record found {user_details.email} - {e}")
            await session.rollback()
            raise DuplicateError
        if not result:
            LOGGER.error("Cooperative User Creation Failed")
            await session.rollback()
            raise CreateError
        await session.commit()
        return schemas.CooperativeUserProfile(**result.as_dict)

async def get_coop_user(email: str):
    async with async_session() as session:
        result = (
            await session.execute(select(CooperativeUser_DB).where(email=email))
        ).scalar_one_or_none()
        if not result:
            raise NotFound
        return schemas.CooperativeUserProfile(**result.as_dict())
    
async def get_coop_user_by_id(coop_user_id: UUID):
    async with async_session() as session:
        result = (
            await session.execute(select(CooperativeUser_DB).where(id=coop_user_id))
        ).scalar_one_or_none()
        if not result:
            raise NotFound
        return schemas.CooperativeUserProfile(**result.as_dict())


async def update_coop_user(coop_user_update: schemas.CooperativeUserUpdate, coop_user_id: UUID):
    async with async_session() as session:
        stmt = (
            update(CooperativeUser_DB)
            .where(CooperativeUser_DB.id == coop_user_id)
            .values(
                coop_user_update.model_dump(
                    exclude_none=True, exclude_unset=True
                )
            )
            .returning(CooperativeUser_DB)
        )
        result = (await session.execute(statement=stmt)).scalar_one_or_none()
        if not result:
            raise UpdateError
        await session.commit()
        return schemas.CooperativeUserProfile(**result.as_dict())

async def delete_coop_user(): ...


async def create_cooperative(cooperative_details: schemas.Cooperative, created_by: UUID, coop_id: str, status: schemas.CooperativeStatus = schemas.CooperativeStatus.ACTIVE):
    async with async_session() as session:
        stmt = insert(Cooperative_DB).values(**cooperative_details.model_dump(), status=status, created_by=created_by, coop_id=coop_id).returning(Cooperative_DB)
        try:
            result = (await session.execute(statement=stmt)).scalar_one_or_none()
        except IntegrityError as e:
            LOGGER.error(f"duplicate record found {cooperative_details.name} - {e}")
            await session.rollback()
            raise DuplicateError
        if not result:
            LOGGER.error("Cooperative User Creation Failed")
            await session.rollback()
            raise CreateError
        await session.commit()
        return schemas.CooperativeProfile(**result.as_dict)
    
async def get_cooperative(id: UUID):
    async with async_session() as session:
        result = (
            await session.execute(select(Cooperative_DB).where(id=id))
        ).scalar_one_or_none()
        if not result:
            raise NotFound
        return schemas.CooperativeProfile(**result.as_dict())
    
async def update_cooperative(cooperative_details: schemas.CooperativeProfileUpdate, id: UUID):
    async with async_session() as session:
        stmt = (
            update(Cooperative_DB)
            .where(Cooperative_DB.id == id)
            .values(
                cooperative_details.model_dump(
                    exclude_none=True, exclude_unset=True
                )
            )
            .returning(Cooperative_DB)
        )
        result = (await session.execute(statement=stmt)).scalar_one_or_none()
        if not result:
            raise UpdateError
        await session.commit()
        return schemas.CooperativeProfile(**result.as_dict())

async def delete_cooperative(): ...

# ------- END OF COOPERATIVE MANAGEMENT ----

async def create_coop_member(member: schemas.Membership, status: schemas.MembershipStatus = schemas.MembershipStatus.PENDING):
    async with async_session() as session:
        stmt = insert(Member_DB).values(member.model_dump(), status=status).returning(Member_DB)
        try:
            result = (await session.execute(statement=stmt)).scalar_one_or_none()
        except IntegrityError as e:
            LOGGER.error(f"duplicate record found for user with {member.user_id} - {e}")
            await session.rollback()
            raise DuplicateError
        if not result:
            LOGGER.error("membership creation/onboarding failed")
            await session.rollback()
            raise CreateError
        await session.commit()
        return schemas.MembershipProfile(**result.as_dict())
    

async def get_coop_membership(membership_id: str):
    async with async_session() as session:
        result = (
            await session.execute(select(Member_DB).where(membership_id=membership_id))
        ).scalar_one_or_none()
        if not result:
            raise NotFound
        return schemas.MembershipProfile(**result.as_dict())
    
async def get_coop_member(coop_member_id: UUID):
    async with async_session() as session:
        result = (
            await session.execute(select(Member_DB).where(membership_id=coop_member_id))
        ).scalar_one_or_none()
        if not result:
            raise NotFound
        return schemas.MembershipProfile(**result.as_dict())

async def update_coop_membership(coop_member_update: schemas.MembershipUpdate, coop_member_id: UUID):
    async with async_session() as session:
        stmt = (
            update(Member_DB)
            .where(Member_DB.id == coop_member_id)
            .values(
                coop_member_update.model_dump(
                    exclude_none=True, exclude_unset=True
                )
            )
            .returning(Member_DB)
        )
        result = (await session.execute(statement=stmt)).scalar_one_or_none()
        if not result:
            raise UpdateError
        await session.commit()
        return schemas.MembershipProfile(**result.as_dict())

async def delete_coop_member(): ...

