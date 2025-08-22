from typing import Optional

from fastapi import APIRouter, Body, Header, status

import theocraft_coop.schemas.cooperative_schemas as schemas
import theocraft_coop.schemas.user_schemas as user_schemas
import theocraft_coop.services.cooperative_service as cooperative_service
from theocraft_coop.root.theocraft_exception import TheocraftBadRequestException

api_router = APIRouter(prefix="/coop/auth", tags=["Cooperative Admin Auth"])

@api_router.post(
    "/sign-up",
    response_model=user_schemas.UserAccessToken,
    status_code=status.HTTP_201_CREATED,
)
async def coop_user_sign_up(user_details: schemas.CooperativeUser):
    if user_details.phone_number is None and user_details.email is None:
        raise TheocraftBadRequestException(
            message="Phone number or email must be provided"
        )
    return await cooperative_service.coop_user_sign_up(user_details)

@api_router.post(
    "/login", response_model=user_schemas.UserAccessToken, status_code=status.HTTP_200_OK
)
async def coop_user_login(login_cred: schemas.Login):
    return await cooperative_service.coop_user_login(
        email=login_cred.email,
        password=login_cred.password,
    )

@api_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    email: schemas.EmailStr = Body(embed=True, default=None, example="sampleuser@website.com")
):
    return await cooperative_service.forgot_password(email=email)

@api_router.post(
    "/password-reset",
    status_code=status.HTTP_200_OK,
    response_model=user_schemas.UserProfile,
)
async def reset_password(
    token: str = Body(embed=True, example=1345),
    new_password: str = Body(embed=True),
):
    user = await cooperative_service.reset_password(token=token, new_password=new_password)
    return user

@api_router.post(
    "/verify-token",
    status_code=status.HTTP_200_OK,
)
async def verify_token(
    code: str = Body(embed=True, example="123456"),
):
    return await cooperative_service.verify_mfa_token(code=code)