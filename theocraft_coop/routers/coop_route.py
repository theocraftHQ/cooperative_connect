'''
Cooperative Creation and Management alongside invitation of users (Admin) to
cooperative 
'''

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Body, Header, status

import theocraft_coop.schemas.cooperative_schemas as schemas
import theocraft_coop.schemas.user_schemas as user_schemas
import theocraft_coop.services.cooperative_service as cooperative_service
from theocraft_coop.root.dependencies import Current_Coop_User
from theocraft_coop.root.theocraft_exception import TheocraftBadRequestException

api_router = APIRouter(prefix="/coop", tags=["Cooperative Admin & Management"])


@api_router.post(
    "/create-coop",
    response_model=schemas.CooperativeProfile,
    status_code=status.HTTP_201_CREATED,
)
async def create_cooperative(coop_details: schemas.Cooperative, current_user_profile: Current_Coop_User):
    return await cooperative_service.create_cooperative(coop_details=coop_details, created_by=current_user_profile.id)

@api_router.get(
    "/coop-profile",
    response_model=schemas.CooperativeProfile,
    status_code=status.HTTP_200_OK,
)
async def cooperative_profile(id: UUID, current_user_profile: Current_Coop_User):
    return await cooperative_service.get_cooperative(id=id)

@api_router.patch(
    "/update-coop",
    response_model=schemas.CooperativeProfile,
    status_code=status.HTTP_201_CREATED,
)
async def update_cooperative(coop_update_details: schemas.CooperativeProfileUpdate, coop_id: UUID, current_user_profile: Current_Coop_User):
    return await cooperative_service.update_cooperative(coop_update=coop_update_details, coop_id=coop_id)


