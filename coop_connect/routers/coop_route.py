"""
Cooperative Creation and Management alongside invitation of users (Admin) to
cooperative
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

import coop_connect.schemas.cooperative_schemas as schemas
import coop_connect.services.cooperative_service as cooperative_service
from coop_connect.root.dependencies import Current_User

api_router = APIRouter(prefix="/coop", tags=["Cooperative Admin & Management"])


@api_router.post(
    "/",
    response_model=schemas.CooperativeProfile,
    status_code=status.HTTP_201_CREATED,
)
async def create_cooperative(
    coop_in: schemas.Cooperative, current_user_profile: Current_User
):
    return await cooperative_service.create_cooperative(
        coop_in=coop_in, created_by=current_user_profile.id
    )


@api_router.get(
    "",
    response_model=schemas.PaginatedCooperativeProfile,
    status_code=status.HTTP_200_OK,
)
async def get_cooperatives(
    current_user: Current_User, paginated_query: schemas.PaginationCoopQuery = Depends()
):
    return await cooperative_service.get_cooperatives(**paginated_query.model_dump())


@api_router.get(
    "/{coop_id}",
    response_model=schemas.CooperativeProfile,
    status_code=status.HTTP_200_OK,
)
async def get_cooperative(coop_id: UUID, current_user_profile: Current_User):
    return await cooperative_service.get_cooperative(id=coop_id)


@api_router.patch(
    "/{coop_id}",
    response_model=schemas.CooperativeProfile,
    status_code=status.HTTP_201_CREATED,
)
async def update_cooperative(
    coop_update_in: schemas.CooperativeUpdate,
    coop_id: UUID,
    current_user: Current_User,
):
    # TODO DEPENDENCY FOR COOPERATIVE MEMBER
    return await cooperative_service.update_cooperative(
        coop_update_in=coop_update_in, coop_id=coop_id, member_id=current_user.id
    )
