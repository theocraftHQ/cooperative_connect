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
from coop_connect.root.coop_enums import MembershipStatus
from coop_connect.schemas.user_schemas import UserProfile
from coop_connect.services.service_utils.exception_collection import (
    NotFound,
    UpdateError,
)

LOGGER = logging.getLogger(__name__)


# ------- START OF COOPERATIVE MANAGEMENT -------


async def get_cooperatives_via_acronym(acronym: str):
    return cooperative_db_handler.get_cooperatives_via_acronym(acronym=acronym)


async def create_cooperative(coop_in: schemas.CooperativeIn, user: UserProfile):

    coop_name = f"{coop_in.acronym.upper()[0:4]}{coop_in.acronym.upper()[4:6]}"
    coop_id = f"COOP-{coop_name.replace(' ','-')}-{str(uuid4()).replace('-', '')[:10]}"
    try:
        await cooperative_db_handler.get_cooperative_via_accronym(
            acronym=coop_in.acronym
        )
        raise ConnectBadRequestException("acroynm is not unique")
    except NotFound:

        try:

            cooperative = await cooperative_db_handler.create_cooperative(
                cooperative_in=schemas.CooperativeExtended(
                    **coop_in.model_dump(exclude="creator_role"),
                    coop_id=coop_id,
                    created_by=user.id,
                    status=schemas.CooperativeStatus.INACTIVE,
                )
            )

            # create root_coop member
            membership_id = f"{coop_name}-{date.today().year}-1"
            referal_code = f"{date.today().year}-1-{str(uuid4()).replace('-', '')[:6]}"

            await cooperative_db_handler.create_coop_member(
                member=schemas.MembershipExtended(
                    membership_id=membership_id,
                    cooperative_id=cooperative.id,
                    onboarding_response=None,
                    user_id=user.id,
                    user_bio=user.bio.id,
                    status=schemas.MembershipStatus.ACTIVE,
                    role=coop_in.creator_role,
                    referal_code=referal_code,
                ),
            )

            return cooperative

        except Exception as e:
            LOGGER.exception(e)
            LOGGER.error("cooperative failed to create")

            raise ConnectBadRequestException(message="cooperative failed to create")


async def get_cooperatives(**kwargs):

    return await cooperative_db_handler.get_cooperatives(**kwargs)


async def get_cooperative_via_acronym(acronym: str):

    try:
        return await cooperative_db_handler.get_cooperative_via_accronym(
            acronym=acronym
        )
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("Cooperative not found")
        raise ConnectNotFoundException(message="cooperative not found")


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
    member_in: schemas.MembershipIn,
    cooperative: schemas.CooperativeProfile,
    user: UserProfile,
):
    if user.bio is None:
        raise ConnectBadRequestException(message="User profile not complete")

    try:
        # THEO-2025-001 [NAME OF COOP, YEAR JOINED, NUMBER IN THE YEAR]

        await _get_coop_member_via_user_id(
            user_id=user.id, cooperative_id=cooperative.id
        )

        raise ConnectBadRequestException(
            message="This user is a member of this cooperative"
        )

    except NotFound:

        return await cooperative_db_handler.create_coop_member(
            member=schemas.MembershipExtended(
                **member_in.model_dump(),
                membership_id=None,
                cooperative_id=cooperative.id,
                user_id=user.id,
                user_bio=user.bio.id,
                referal_code=None,
                status=schemas.MembershipStatus.PENDING_APPROVAL,
                role=schemas.CooperativeUserRole.MEMBER,
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
    try:
        cooperative_member = await _get_coop_member_via_user_id(
            user_id=user_id, cooperative_id=cooperative_id
        )
        return cooperative_member.role, cooperative_member.status
    except NotFound:
        raise ConnectNotFoundException(message="user is not a member of cooperative")


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
    offset: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    year: Optional[schemas.Years] = None,
) -> schemas.PaginatedMembersResponse:

    return await cooperative_db_handler.get_all_members(
        id=cooperative_id,
        **{
            "status": status,
            "offset": offset,
            "limit": limit,
            "years": year,
            "search": search,
        },
    )


async def update_coop_membership(
    cooperative_id: UUID, member_id: UUID, member_update: schemas.MembershipUpdate
):
    try:
        cooperative_member_profile = await get_coop_member(
            member_id=member_id, cooperative_id=cooperative_id
        )

        member_update = schemas.MembershipExtendedUpdate(
            **member_update.model_dump(),
            membership_id=None,
            referal_code=None,
        )

        if member_update.status == MembershipStatus.ACTIVE:
            coop_name = cooperative_member_profile.cooperative.acronym.upper()[0:4]

            all_members = await get_all_coop_members(
                cooperative_id=cooperative_id, year=date.today().year
            )
            # create root_coop member
            member_update.membership_id = (
                f"{coop_name}-{date.today().year}-{all_members.total_count+1}"
            )

            member_update.referal_code = f"{date.today().year}-{all_members.total_count+1}-{str(uuid4()).replace('-', '')[:6]}"

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
