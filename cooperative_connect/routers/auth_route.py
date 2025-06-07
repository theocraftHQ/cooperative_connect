from fastapi import APIRouter, Body, Header, status
from pydantic import constr

import cooperative_connect.schemas.user_schemas as schemas
import cooperative_connect.services.user_service as user_service
from cooperative_connect.root.dependencies import Current_User, get_new_access_token

api_router = APIRouter(prefix="/auth", tags=["User"])


@api_router.post(
    "/sign-up",
    response_model=schemas.UserAccessToken,
    status_code=status.HTTP_201_CREATED,
)
async def sign_up(admin_user: schemas.User):
    return await user_service.sign_up(admin_user=admin_user)


@api_router.post(
    "/login", response_model=schemas.UserAccessToken, status_code=status.HTTP_200_OK
)
async def login(login_cred: schemas.Login):
    return await user_service.login(
        email=login_cred.email, password=login_cred.password
    )


@api_router.post(
    "/me", response_model=schemas.UserProfile, status_code=status.HTTP_200_OK
)
async def me(current_user_profile: Current_User):
    return schemas.UserProfile(**current_user_profile.as_dict())


@api_router.get(
    "/refresh-token",
    response_model=schemas.UserAccessToken,
    status_code=status.HTTP_200_OK,
)
async def new_access_token(refresh_token: str = Header(convert_underscores=False)):
    return schemas.UserAccessToken(
        access_token=await get_new_access_token(token=refresh_token),
        refresh_token=refresh_token,
    )


@api_router.post("/logout", status_code=status.HTTP_200_OK)
async def admin_logout(
    token_cred: schemas.UserAccessToken,
    user: Current_User,
):
    return await user_service.logout(
        access_token=token_cred.access_token, refresh_token=token_cred.refresh_token
    )


@api_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    email: schemas.EmailStr = Body(embed=True, default=None, example="agent@gr.com"),
    phone_number: schemas.PhoneNumber = Body(embed=True),
):
    return await user_service.forgot_password(email=email)


@api_router.post(
    "/password-reset",
    status_code=status.HTTP_200_OK,
    response_model=schemas.AdminUserProfile,
)
async def reset_password(
    token: constr(max_length=4, min_length=4) = Body(embed=True, example=1345),
    new_password: str = Body(embed=True),
):
    return await user_service.reset_password(token=token, new_password=new_password)
