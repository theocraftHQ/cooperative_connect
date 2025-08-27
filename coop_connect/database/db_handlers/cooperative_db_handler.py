import logging
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import and_, delete, extract, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

import coop_connect.schemas.cooperative_schemas as schemas
from coop_connect.database.orms.cooperative_orm import Cooperative as Cooperative_DB
from coop_connect.database.orms.cooperative_orm import Member as Member_DB
from coop_connect.root.database import async_session
from coop_connect.services.service_utils.exception_collection import (
    CreateError,
    DuplicateError,
    NotFound,
    UpdateError,
)

LOGGER = logging.getLogger(__name__)


async def create_cooperative(
    cooperative_in: schemas.CooperativeExtended,
):
    async with async_session() as session:
        stmt = (
            insert(Cooperative_DB)
            .values(
                **cooperative_in.model_dump(),
            )
            .returning(Cooperative_DB)
        )
        try:
            result = (await session.execute(statement=stmt)).scalar_one_or_none()
        except IntegrityError as e:
            LOGGER.error(f"duplicate record found {cooperative_in.name} - {e}")
            await session.rollback()
            raise DuplicateError
        if not result:
            LOGGER.error("Cooperative User Creation Failed")
            await session.rollback()
            raise CreateError
        await session.commit()
        return schemas.CooperativeProfile(**result.as_dict())


async def get_cooperative(id: UUID):  # user_id: UUID
    async with async_session() as session:
        result = (
            await session.execute(select(Cooperative_DB).where(Cooperative_DB.id == id))
        ).scalar_one_or_none()
        if not result:
            raise NotFound
        return schemas.CooperativeProfile(**result.as_dict())


async def get_cooperatives(**kwargs):

    public_listing = kwargs.get("public_listing")
    search = kwargs.get("search")
    offset = kwargs.get("offset", 0)
    limit = kwargs.get("limit", 20)

    filter_array = []
    if public_listing:

        filter_array.append(Cooperative_DB.public_listing == public_listing)
    if search:
        filter_array.append(Cooperative_DB.name.ilike(f"%{search}%"))

    async with async_session() as session:

        statement = (
            select(Cooperative_DB)
            .filter(and_(filter_array))
            .offset(offset=offset)
            .limit(limit=limit)
        )

        result = (await session.execute(statement=statement)).scalars().all()

        if not result:

            return schemas.PaginatedCooperativeProfile()

        total_count = (
            await session.execute(
                select(func.count(Cooperative_DB.id)).filter(
                    Cooperative_DB.public_listing == public_listing
                )
            )
        ).scalar()
        return schemas.PaginatedCooperativeProfile(
            result_set=[
                schemas.CooperativeProfile(**coop.as_dict()) for coop in result
            ],
            result_count=total_count,
            page=offset + 1,
            page_size=len(result),
            total_count=total_count,
        )


async def update_cooperative(
    cooperative_details: schemas.CooperativeUpdate, coop_id: UUID
):
    async with async_session() as session:
        stmt = (
            update(Cooperative_DB)
            .where(Cooperative_DB.id == coop_id)
            .values(
                cooperative_details.model_dump(exclude_none=True, exclude_unset=True)
            )
            .returning(Cooperative_DB)
        )
        result = (await session.execute(statement=stmt)).scalar_one_or_none()
        if not result:
            await session.rollback()
            raise UpdateError

        await session.commit()

        return schemas.CooperativeProfile(**result.as_dict())


async def delete_cooperative(): ...


# ------- END OF COOPERATIVE MANAGEMENT ----


# ------- START OF COOP MEMBER HANDLER MANAGEMENT -------
async def create_coop_member(
    member: schemas.MembershipExtended,
):
    async with async_session() as session:
        stmt = insert(Member_DB).values(member.model_dump()).returning(Member_DB)
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


async def get_coop_member_via_user_id(user_id: UUID, cooperative_id: UUID):
    async with async_session() as session:
        result = (
            await session.execute(
                select(Member_DB).where(
                    and_(
                        Member_DB.user_id == user_id,
                        Member_DB.cooperative_id == cooperative_id,
                    )
                )
            )
        ).scalar_one_or_none()
        if not result:
            raise NotFound
        return schemas.MembershipProfile(**result.as_dict())


async def get_coop_member(id: UUID, cooperative_id: UUID):
    async with async_session() as session:
        result = (
            await session.execute(
                select(Member_DB).where(
                    and_(Member_DB.id == id, Member_DB.cooperative_id == cooperative_id)
                )
            )
        ).scalar_one_or_none()
        if not result:
            raise NotFound
        return schemas.MembershipProfile(**result.as_dict())


async def get_all_members(id: UUID, **kwargs):

    filter_array = []

    offset = kwargs.get("offset", 0)
    limit = kwargs.get("limit", 20)
    years = kwargs.get("years", 0)
    status = kwargs.get("status")

    if years:
        filter_array.append(extract("year", Member_DB.date_created_utc) == years)
    if status:
        filter_array.append(Member_DB.status == schemas.MembershipStatus(status))

    async with async_session() as session:
        base_query = (
            select(Member_DB)
            .where(and_(Member_DB.cooperative_id == id, *filter_array))
            .offset(offset=offset)
            .limit(limit=limit)
        )

        result = (await session.execute(base_query)).scalars().all()

        if not result:
            return schemas.PaginatedMembersResponse()

        total_count = (
            await session.execute(
                statement=select(func.count(Member_DB.id)).filter(
                    Member_DB.cooperative_id == id,
                )
            )
        ).scalar() or 0

        return schemas.PaginatedMembersResponse(
            result_set=[schemas.MembershipProfile(**m.as_dict()) for m in result],
            result_size=len(result),
            total_count=total_count,
            page=(offset // limit) + 1,
        )


async def update_coop_membership(
    coop_member_update: schemas.MembershipUpdate, coop_member_id: UUID, coop_id: UUID
):
    async with async_session() as session:
        stmt = (
            update(Member_DB)
            .where(
                and_(
                    Member_DB.id == coop_member_id, Member_DB.cooperative_id == coop_id
                )
            )
            .values(
                coop_member_update.model_dump(exclude_none=True, exclude_unset=True)
            )
            .returning(Member_DB)
        )
        result = (await session.execute(statement=stmt)).scalar_one_or_none()
        if not result:
            await session.rollback()
            raise UpdateError
        await session.commit()
        return schemas.MembershipProfile(**result.as_dict())


async def delete_coop_member(): ...


# ------- END OF COOP MEMBER HANDLER MANAGEMENT -------
