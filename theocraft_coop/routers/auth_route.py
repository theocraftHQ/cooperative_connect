from fastapi import APIRouter, Body, Header, status

import theocraft_coop.schemas.user_schemas as schemas
import theocraft_coop.services.user_service as user_service
from theocraft_coop.root.connect_enums import UserType
from theocraft_coop.root.dependencies import Current_User, get_new_access_token
from theocraft_coop.root.utils.base_schemas import AbstractResponse

api_router = APIRouter(prefix="/auth", tags=["User"])


@api_router.post(
    "/mfa-sign-up",
    response_model=AbstractResponse,
    status_code=status.HTTP_201_CREATED,
)
async def user_sign_up(phone_number: schemas.PhoneNumber):
    return await user_service.user_mfa_sign_up(phone_number=phone_number)


@api_router.post(
    "/sign-up",
    response_model=schemas.UserAccessToken,
    status_code=status.HTTP_201_CREATED,
)
async def sign_up(
    user_in: schemas.UserOnboard, user_type: UserType = UserType.coop_member
):

    user_in.user_type = user_type
    if user_in.user_type == UserType.coop_admin:
        return await user_service.onboard_user(user_onboard=user_in)

    return await user_service.sign_up(
        user_in=schemas.User(**user_in.model_dump(exclude="user_bio"))
    )


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
