from typing import Optional

from fastapi import APIRouter, Body, Header, status

import coop_connect.schemas.user_schemas as schemas
import coop_connect.services.user_service as user_service
from coop_connect.root.connect_exception import ConnectBadRequestException
from coop_connect.root.coop_enums import UserType
from coop_connect.root.dependencies import Current_User, get_new_access_token
from coop_connect.root.utils.base_schemas import AbstractResponse

api_router = APIRouter(prefix="/auth", tags=["User"])


@api_router.post(
    "/mfa-sign-up",
    response_model=AbstractResponse,
    status_code=status.HTTP_201_CREATED,
)
async def user_sign_up(
    phone_number: Optional[schemas.PhoneNumber] = Body(embed=True, default=None),
    email: Optional[schemas.EmailStr] = Body(embed=True, default=None),
):
    if phone_number is None and email is None:
        raise ConnectBadRequestException(
            message="phone number or email must be provided"
        )

    return await user_service.user_mfa_sign_up(phone_number=phone_number, email=email)


@api_router.post(
    "/sign-up",
    response_model=schemas.UserAccessToken,
    status_code=status.HTTP_201_CREATED,
)
async def sign_up(
    user_in: schemas.UserOnboard, user_type: UserType = UserType.COOP_MEMBER
):

    user_in.user_type = user_type
    if user_in.user_type == UserType.COOP_ADMIN:
        return await user_service.onboard_user(user_onboard=user_in)

    return await user_service.sign_up(
        user_in=schemas.User(**user_in.model_dump(exclude="user_bio"))
    )


@api_router.post(
    "/admin-sign-up",
    response_model=schemas.UserAccessToken,
    status_code=status.HTTP_201_CREATED,
)
async def admin_sign_up(user_in: schemas.User):

    user_in.user_type = UserType.ADMIN

    return await user_service.sign_up(user_in=user_in)


@api_router.post(
    "/login", response_model=schemas.UserAccessToken, status_code=status.HTTP_200_OK
)
async def login(login_cred: schemas.Login):
    return await user_service.login(
        email=login_cred.email,
        phone_number=login_cred.phone_number,
        password=login_cred.password,
    )


@api_router.post(
    "/me", response_model=schemas.UserProfile, status_code=status.HTTP_200_OK
)
async def me(current_user_profile: Current_User):
    return current_user_profile


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


@api_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    email: schemas.EmailStr = Body(embed=True, default=None, example="agent@gr.com"),
    phone_number: schemas.PhoneNumber = Body(embed=True),
):
    return await user_service.forgot_password(email=email, phone_number=phone_number)


@api_router.post(
    "/password-reset",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserProfile,
)
async def reset_password(
    token: str = Body(embed=True, example=1345),
    new_password: str = Body(embed=True),
):
    user = await user_service.reset_password(token=token, new_password=new_password)
    return user


@api_router.post(
    "/verify-token",
    status_code=status.HTTP_200_OK,
)
async def verify_token(
    code: str = Body(embed=True, example="123456"),
):
    return await user_service.verify_mfa_token(code=code)


@api_router.patch(
    "/onboard",
    response_model=schemas.UserProfile,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_update: schemas.UserUpdate, current_user_profile: Current_User
):
    return await user_service.user_update(
        user_update=user_update, user_id=current_user_profile.id
    )
