import logging
from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

import coop_connect.database.db_handlers.cooperative_db_handler as cooperative_db_handler
import coop_connect.schemas.cooperative_schemas as schemas
from coop_connect.root.connect_exception import (
    ConnectBadRequestException,
    ConnectNotFoundException,
)
from coop_connect.services.service_utils.exception_collection import (
    NotFound,
    UpdateError,
)

LOGGER = logging.getLogger(__name__)


# ------- START OF COOPERATIVE MANAGEMENT -------
async def create_cooperative(coop_in: schemas.CooperativeIn, created_by: UUID):

    coop_name = coop_in.name.upper()[0:4]
    coop_id = f"COOP-{coop_name}-{str(uuid4()).random(length=10)}"
    try:

        cooperative = await cooperative_db_handler.create_cooperative(
            cooperative_in=schemas.CooperativeExtended(
                **coop_in.model_dump(exclude="creator_role"),
                coop_id=coop_id,
                created_by=created_by,
            )
        )

        # create root_coop member
        membership_id = f"{coop_name}-{date.today().year}-001"

        await cooperative_db_handler.create_coop_member(
            member=schemas.MembershipExtended(
                membership_id=membership_id,
                cooperative_id=cooperative.id,
                user_id=created_by,
                status=schemas.MembershipStatus.ACTIVE,
                role=coop_in.creator_role,
            ),
        )

        return cooperative

    except Exception as e:
        LOGGER.exception(e)
        LOGGER.error("cooperative failed to create")

        raise ConnectBadRequestException(message="cooperative failed to create")


async def get_cooperatives(**kwargs):

    return await cooperative_db_handler.get_cooperatives(**kwargs)


async def get_cooperative(id: UUID):
    try:
        return await cooperative_db_handler.get_cooperative(id=id)
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("Cooperative not found")
        raise ConnectNotFoundException(message="cooperative not found")


async def update_cooperative(
    coop_update_in: schemas.CooperativeUpdate, coop_id: UUID, member_id: UUID
):
    try:
        cooperative = await get_cooperative(id=coop_id)
        meta_data = cooperative.meta if cooperative.meta else {}

        if meta_data.get("update_trail"):
            update_trail: list = meta_data.get("updated_by")
            values = []

            if coop_update_in.public_listing:
                values.append("Public Listing")

            if coop_update_in.onboarding_requirements:
                values.append("Onboarding Requirements")

            update_trail.append(
                {
                    "date_updated": str(datetime.utcnow()),
                    "updated_by": member_id,
                    "values": values,
                }
            )
        else:

            values = []

            if coop_update_in.public_listing:
                values.append("Public Listing")

            if coop_update_in.onboarding_requirements:
                values.append("Onboarding Requirements")

            update_trail = [
                {
                    "date_updated": str(datetime.utcnow()),
                    "updated_by": member_id,
                    "values": values,
                }
            ]

        meta_data["update_trail"] = update_trail[::-1]

        coop_update_in.meta = meta_data
        coop_update = await cooperative_db_handler.update_cooperative(
            cooperative_details=coop_update_in, coop_id=coop_id
        )
        return coop_update
    except UpdateError as e:
        LOGGER.exception(e)
        LOGGER.error("Unexplainable cooperative profile update error")
        raise ConnectBadRequestException(message="cooperative failed to update")


# ------- START OF COOP MEMBER MANAGEMENT -------


async def create_coop_member(
    member_in: schemas.MembershipIn, cooperative: schemas.CooperativeProfile
):

    try:
        # THEO-2025-001 [NAME OF COOP, YEAR JOINED, NUMBER IN THE YEAR]

        await _get_coop_member_via_user_id(
            user_id=member_in.user_id, cooperative_id=cooperative.id
        )

        raise ConnectBadRequestException(
            message="This user is a member of this cooperative"
        )

    except NotFound:
        coop_name = cooperative.name.upper()[0:4]

        all_members = await get_all_coop_members(
            cooperative_id=cooperative.id, year=date.today().year
        )

        # create root_coop member
        membership_id = f"{coop_name}-{date.today().year}-{all_members.total_count+1}"

        return await cooperative_db_handler.create_coop_member(
            member=schemas.MembershipExtended(
                **member_in.model_dump(),
                membership_id=membership_id,
                cooperative_id=cooperative.id,
            ),
        )


async def _get_coop_member_via_user_id(user_id: UUID, cooperative_id: UUID):

    try:

        return await cooperative_db_handler.get_coop_member_via_user_id(
            user_id=user_id, cooperative_id=cooperative_id
        )
    except NotFound as e:

        raise e


async def get_coop_member_role(user_id: UUID, cooperative_id: UUID):

    cooperative_member = await _get_coop_member_via_user_id(
        user_id=user_id, cooperative_id=cooperative_id
    )
    return cooperative_member.membership_type


async def get_coop_member(member_id: UUID, cooperative_id: UUID):
    try:
        return await cooperative_db_handler.get_coop_member(
            id=member_id, cooperative_id=cooperative_id
        )
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("Member Not found")
        raise ConnectNotFoundException(message="Member not found for this cooperative")


async def get_all_coop_members(
    cooperative_id: UUID,
    status: Optional[schemas.MembershipStatus] = None,
    offset: int = 1,
    limit: int = 20,
    year: Optional[schemas.Years] = None,
) -> schemas.PaginatedMembersResponse:

    return await cooperative_db_handler.get_all_members(
        id=cooperative_id,
        **{"status": status, "offset": offset, "limit": limit, "year": year},
    )


async def update_coop_membership(
    cooperative_id: UUID, member_id: UUID, member_update: schemas.MembershipUpdate
):
    try:
        await get_coop_member(member_id=member_id, cooperative_id=cooperative_id)
        coop_member_update = await cooperative_db_handler.update_coop_membership(
            coop_member_update=member_update,
            coop_member_id=member_id,
            coop_id=cooperative_id,
        )
        return coop_member_update
    except UpdateError as e:
        LOGGER.exception(e)
        LOGGER.error("Unexplainable cooperative member profile update error")
        raise ConnectBadRequestException(
            message="cooperative member profile update failed"
        )


# ------- END OF COOP MEMBER MANAGEMENT -------
