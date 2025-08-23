'''
Management of membership profile and 
'''

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Body, Header, Query, status

import theocraft_coop.schemas.cooperative_schemas as schemas
import theocraft_coop.services.cooperative_service as cooperative_service
from theocraft_coop.root.dependencies import Current_Coop_User
from theocraft_coop.root.theocraft_exception import TheocraftBadRequestException

api_router = APIRouter(prefix="/member", tags=["Cooperative Membership Management"])

@api_router.get(
    "/all-members",
    response_model=schemas.PaginatedMembersResponse,
    status_code=status.HTTP_200_OK,
)
async def all_coop_member(
    cooperative_id: UUID,
    current_user_profile: Current_Coop_User,
    status_filter: Optional[schemas.MembershipStatus] = Query(None, description="Filter members by status"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)")
):
    return await cooperative_service.get_all_coop_members(
        cooperative_id=cooperative_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size
    )

@api_router.get(
    "/get-member-profile",
    response_model=schemas.MembershipProfile,
    status_code=status.HTTP_200_OK,
)
async def get_coop_membership(member_id: UUID, cooperative_id: UUID, current_user_profile: Current_Coop_User):
    return await cooperative_service.get_coop_member(member_id=member_id, cooperative_id=cooperative_id)

@api_router.patch(
    "/update-member",
    response_model=schemas.MembershipProfile,
    status_code=status.HTTP_200_OK,
)
async def update_membership(member_update: schemas.MembershipUpdate, current_user_profile: Current_Coop_User):
    return await cooperative_service.update_coop_membership(member_update=member_update)

