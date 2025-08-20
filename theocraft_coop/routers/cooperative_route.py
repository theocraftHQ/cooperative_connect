from typing import Optional

from fastapi import APIRouter, Body, Header, status

import theocraft_coop.schemas.user_schemas as schemas
import theocraft_coop.services.cooperative_service as cooperative_service

api_router = APIRouter(prefix="/coop", tags=["Cooperative Admin & Management"])


@api_router.get(
    "/a-coop",
    status_code=status.HTTP_200_OK,
)
async def a_cooperative(id):
    return await cooperative_service.get_cooperative(id=id)


@api_router.get(
    "/user",
    status_code=status.HTTP_200_OK,
)
async def cooperative_user(id):
    return await cooperative_service.get_cooperative_user(id=id)

@api_router.get(
    "/member",
    status_code=status.HTTP_200_OK,
)
async def cooperative_member(id):
    return await cooperative_service.get_cooperative_member(id=id)