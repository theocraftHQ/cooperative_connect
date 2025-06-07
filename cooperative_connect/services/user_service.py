import logging
from uuid import UUID

from fastapi import HTTPException

import cooperative_connect.database.db_handlers.user_db_handler as user_db_handler
import cooperative_connect.root.dependencies as dep
import cooperative_connect.schemas.user_schemas as schemas
import cooperative_connect.services.service_utils.auth_utils as auth_utils
import cooperative_connect.services.service_utils.gr_redis_utils as redis_utils
import cooperative_connect.services.service_utils.token_utils as toks_utils
from cooperative_connect.services.service_utils.exception_collection import (
    NotFound,
    UpdateError,
)

LOGGER = logging.getLogger(__name__)


async def get_user_via_unique(email: str = None, phone_number: str = None):
    try:
        return await user_db_handler.get_user(email=email, phone_number=phone_number)
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("account not found")
        raise HTTPException()


async def get_user(id: UUID):
    try:
        return await user_db_handler.get_user(id=id)
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("Agent not found")

        raise HTTPException()


# create record
async def sign_up(user_in: schemas.User):

    user_in.password = auth_utils.hash_password(plain_password=user_in.password)

    user_profile = await user_db_handler.create_user(user=user_in)
    user_profile_dict = {"id": str(user_profile.id)}
    access_token, refresh_token = (
        dep.create_access_token(data=user_profile_dict),
        dep.create_refresh_token(data=user_profile_dict),
    )

    return schemas.UserAccessToken(
        access_token=access_token, refresh_token=refresh_token
    )


# login
async def login(email: str, password: str):
    user_profile = await get_user_via_unique(email=email)
    if not auth_utils.verify_password(
        hashed_password=user_profile.password, plain_password=password
    ):
        raise HTTPException()

    payload_dict = {"id": str(user_profile.id)}
    access_token, refresh_token = dep.create_access_token(
        data=payload_dict
    ), dep.create_refresh_token(data=payload_dict)

    return schemas.UserAccessToken(
        access_token=access_token, refresh_token=refresh_token
    )


# forget password
async def forgot_password(email: str):
    await get_user_via_unique(email=email)

    # Create a Token 4 OTP
    token = toks_utils.gr_token_gen()

    redis_utils.add_forget_token(token=token, email=email)
    # send mail

    # await send_mail(
    #     subject="Forgot Password",
    #     reciepients=[email],
    #     payload={"token": token},
    #     template="user_auth/token_email_template.html",
    # )
    return {"messge": "mail sent"}

    ...


async def user_update(user_update: schemas.UserUpdate, user_id: UUID):
    try:
        return await user_db_handler.update_user(
            user_update=user_update, user_id=user_id
        )
    except UpdateError as e:
        LOGGER.exception(e)
        LOGGER.error("unexplainable update error")
        raise HTTPException()


async def reset_password(token: int, new_password: str) -> user_db_handler.User_DB:
    email = redis_utils.get_forget_token(token=token)
    if not email:
        LOGGER.error(f"forgot password token: {token} not valid")
        raise HTTPException()

    user_profile = await get_user_via_unique(email=email)

    new_password = auth_utils.hash_password(plain_password=new_password)
    updated_user_profile = await user_update(
        admin_update=schemas.UserUpdate(password=new_password),
        admin_user_uid=user_profile.id,
    )
    return updated_user_profile


async def logout(access_token: str, refresh_token: str):
    redis_utils.add_token_blacklist(
        access_token=access_token, refresh_token=refresh_token
    )

    return {}
