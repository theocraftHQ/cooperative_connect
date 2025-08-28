"""
Management of membership profile and
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

import coop_connect.schemas.cooperative_schemas as schemas
import coop_connect.services.cooperative_service as cooperative_service
from coop_connect.root.dependencies import Current_User, CurrentUnprotectedCooperative
from coop_connect.root.permission import (
    CoopAllRoles,
    CoopGeneralPerm,
    PermissionsDependency,
)

api_router = APIRouter(
    prefix="/coop/{coop_id}/members", tags=["Cooperative Membership Management"]
)


@api_router.post(
    "/",
    response_model=schemas.MembershipProfile,
    status_code=status.HTTP_200_OK,
)
async def join_cooperative(
    coop_id: UUID,
    membership_in: schemas.MembershipIn,
    current_user: Current_User,
    cooperative: CurrentUnprotectedCooperative,
):
    return await cooperative_service.create_coop_member(
        cooperative_id=coop_id,
        member_in=membership_in,
    )


@api_router.get(
    "",
    response_model=schemas.PaginatedMembersResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionsDependency([CoopAllRoles]))],
)
async def all_coop_member(
    coop_id: UUID,
    current_user: Current_User,
    pagination_query: schemas.PaginationMembCoopQuery = Depends(),
):
    return await cooperative_service.get_all_coop_members(
        cooperative_id=coop_id, **pagination_query.model_dump()
    )


@api_router.get(
    "/{member_id}",
    response_model=schemas.MembershipProfile,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionsDependency([CoopAllRoles]))],
)
async def get_coop_membership(
    member_id: UUID,
    coop_id: UUID,
    current_user: Current_User,
):
    return await cooperative_service.get_coop_member(
        member_id=member_id, cooperative_id=coop_id
    )


@api_router.patch(
    "/{member_id}",
    response_model=schemas.MembershipProfile,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionsDependency([CoopGeneralPerm]))],
)
async def update_membership(
    member_id: UUID,
    coop_id: UUID,
    member_update: schemas.MembershipUpdate,
    current_user: Current_User,
):
    return await cooperative_service.update_coop_membership(
        member_update=member_update, member_id=member_id, cooperative_id=coop_id
    )
