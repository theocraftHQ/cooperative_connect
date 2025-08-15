import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException

import theocraft_coop.database.db_handlers.user_db_handler as user_db_handler
import theocraft_coop.root.dependencies as dep
import theocraft_coop.schemas.user_schemas as schemas
import theocraft_coop.services.service_utils.auth_utils as auth_utils
import theocraft_coop.services.service_utils.token_utils as toks_utils
from theocraft_coop.root.theocraft_exception import (
    TheocraftAuthException,
    TheocraftBadRequestException,
    TheocraftNotFoundException,
)
from theocraft_coop.root.utils.ebulk_sms import send_sms
from theocraft_coop.root.utils.send_mail import send_mail
from theocraft_coop.services.service_utils.exception_collection import (
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
        raise e


async def get_user(id: UUID):
    try:
        return await user_db_handler.get(user_id=id)
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("user not found")

        raise TheocraftNotFoundException(message="user not found")


async def user_mfa_sign_up(phone_number: Optional[schemas.PhoneNumber] = None, email: Optional[schemas.EmailStr] = None):  # type: ignore

    try:
        await get_user_via_unique(phone_number=phone_number)
        raise TheocraftBadRequestException(message="phone_number exist for user")

    except NotFound:
        code = toks_utils.token_gen()
        try:
            await user_db_handler.get_mfa_token_via_user_info(phone_number=phone_number)
            raise TheocraftBadRequestException(
                message="mfa token already exists for this phone number"
            )
        except NotFound:

            mfa_token = await user_db_handler.create_mfa_token(
                phone_number=phone_number, code=code
            )
            if mfa_token.phone_number:
                await send_sms(
                    message=f"{mfa_token.code}", phone_number=mfa_token.phone_number
                )

            if mfa_token.email:
                await send_mail(
                    subject="MFA Token for Signup on Theocraft Coop",
                    reciepients=[email],
                    payload={"token": code},
                    template="user_auth/token_email_template.html",
                )

            return {
                "message": "mfa token created and sent",
            }


async def resend_token(phone_number: str = None, email: str = None):
    if phone_number is None and email is None:
        raise TheocraftBadRequestException(
            message="phone number and email can not be null"
        )

    mfa_token = await user_db_handler.get_mfa_token_via_user_info(
        phone_number=phone_number, email=email
    )

    if datetime.now(tz=timezone.utc) > mfa_token.code_expires_at:

        mfa_token = await user_db_handler.create_mfa_token(
            phone_number=mfa_token.phone_number,
            email=mfa_token.email,
            code=toks_utils.token_gen(),
        )
        if mfa_token.phone_number:
            await send_sms(
                message=f"{mfa_token.code}", phone_number=mfa_token.phone_number
            )

        if mfa_token.email:
            await send_mail(
                subject="MFA Token for Signup on Theocraft Coop",
                reciepients=[email],
                payload={"token": mfa_token.code},
                template="user_auth/token_email_template.html",
            )

        return

    if mfa_token.phone_number:
        await send_sms(message=f"{mfa_token.code}", phone_number=mfa_token.phone_number)

    if mfa_token.email:
        await send_mail(
            subject="MFA Token for Signup on Theocraft Coop",
            reciepients=[email],
            payload={"token": mfa_token.code},
            template="user_auth/token_email_template.html",
        )


async def verify_mfa_token(code: str):
    mfa_token = await user_db_handler.get_mfa_token(code=code)
    if datetime.now() > mfa_token.code_expires_at:
        await user_db_handler.delete_mfa_token(id=mfa_token.id)
        code = toks_utils.token_gen()
        mfa_token = await user_db_handler.create_mfa_token(
            phone_number=mfa_token.phone_number, email=mfa_token.email, code=code
        )
        if mfa_token.phone_number:
            await send_sms(
                message=f"{mfa_token.code}", phone_number=mfa_token.phone_number
            )

        if mfa_token.email:
            pass

        raise TheocraftBadRequestException(message="verification code has expired")

    await user_db_handler.update_mfa_token(id=mfa_token.id, verified=True)

    return


async def onboard_user(user_onboard: schemas.UserOnboard):

    if user_onboard.email is None and user_onboard.phone_number is None:

        raise TheocraftBadRequestException(
            message="email and phone number can not be null"
        )
    try:
        if user_onboard.email is not None:
            await get_user_via_unique(email=user_onboard.email)

        if user_onboard.phone_number is not None:
            await get_user_via_unique(phone_number=user_onboard.phone_number)

        raise TheocraftBadRequestException(
            message="user already exists with this email or phone number"
        )

    except NotFound:
        # user does not exist, create a new user
        sign_up_tokens = await sign_up(
            user=schemas.User(
                first_name=user_onboard.first_name,
                last_name=user_onboard.last_name,
                email=user_onboard.email,
                phone_number=user_onboard.phone_number,
                password=user_onboard.password,
                user_type=user_onboard.user_type,
            )
        )
        user_read = await get_user_via_unique(
            email=user_onboard.email, phone_number=user_onboard.phone_number
        )
        if user_onboard.user_bio is not None:
            await user_db_handler.create_user_bio(
                user_id=user_read.id, user_bio=user_onboard.user_bio
            )

        return sign_up_tokens
        #


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
async def login(
    password: str, email: Optional[str] = None, phone_number: Optional[str] = None
):
    if email is None and phone_number is None:
        raise TheocraftBadRequestException(
            message="email and phone number can not be null"
        )
    user_profile = await get_user_via_unique(email=email)
    if not auth_utils.verify_password(
        hashed_password=user_profile.password, plain_password=password
    ):
        raise TheocraftAuthException(message="email or password is incorrect")

    payload_dict = {"id": str(user_profile.id)}
    access_token, refresh_token = dep.create_access_token(
        data=payload_dict
    ), dep.create_refresh_token(data=payload_dict)

    return schemas.UserAccessToken(
        access_token=access_token, refresh_token=refresh_token
    )


async def update_user_bio(user_bio: schemas.UserBio, user_read: schemas.UserProfile):
    if user_read.bio is None:
        # create user bio
        return await user_db_handler.create_user_bio(
            user_bio=user_bio, user_id=user_read.id
        )
    return await user_db_handler.update_user_bio(
        user_bio=user_bio, user_id=user_read.id
    )


async def user_update(user_update: schemas.UserUpdate, user_id: UUID):
    try:
        user = await user_db_handler.update_user(
            user_update=user_update, user_id=user_id
        )
        user = await get_user(id=user.id)
        if user_update.user_bio is not None:
            user_bio = await update_user_bio(
                user_bio=user_update.user_bio, user_read=user
            )
            user.bio = user_bio

        return user

    except UpdateError as e:
        LOGGER.exception(e)
        LOGGER.error("unexplainable update error")
        raise TheocraftBadRequestException(message="user update failed")


async def reset_password(code: int, new_password: str) -> user_db_handler.User_DB:

    try:
        mfa_token_read = await user_db_handler.get_mfa_token(code=code)
        await verify_mfa_token(code=mfa_token_read.code)

        user_profile = await get_user_via_unique(
            email=mfa_token_read.email, phone_number=mfa_token_read.phone_number
        )

        new_password = auth_utils.hash_password(plain_password=new_password)
        updated_user_profile = await user_update(
            admin_update=schemas.UserUpdate(password=new_password),
            admin_user_uid=user_profile.id,
        )
        return updated_user_profile
    except NotFound:
        LOGGER.error(f"forgot password token: {code} not valid")
        raise TheocraftNotFoundException(
            message=f"forgot password token: {code} not valid"
        )


# forget password
async def forgot_password(
    email: Optional[str] = None, phone_number: Optional[str] = None
):

    if email is None and phone_number is None:
        raise TheocraftBadRequestException(
            message="email and phone number can not be null"
        )

    if email is not None:
        await get_user_via_unique(email=email)
    if phone_number is not None:
        await get_user_via_unique(phone_number=phone_number)

    # Create a Token 4 OTP
    code = toks_utils.token_gen()

    mfa_code_read = await user_db_handler.create_mfa_token(
        code=code, email=email, phone_number=phone_number
    )

    if mfa_code_read.phone_number:
        await send_sms(
            message=f"{mfa_code_read.code}", phone_number=mfa_code_read.phone_number
        )
    if mfa_code_read.email:
        # send mail
        await send_mail(
            subject="Forgot Password",
            reciepients=[email],
            payload={"token": mfa_code_read.code},
            template="user_auth/token_email_template.html",
        )

    return {"messge": "otp sent"}
