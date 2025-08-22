import logging
import math
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from shortuuid import ShortUUID

from fastapi import HTTPException

import theocraft_coop.database.db_handlers.cooperative_db_handler as cooperative_db_handler
import theocraft_coop.database.db_handlers.user_db_handler as user_db_handler
import theocraft_coop.root.dependencies as dep
import theocraft_coop.schemas.cooperative_schemas as schemas
import theocraft_coop.schemas.user_schemas as user_schemas
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

# ------- START OF COOP USER AUTH -------
async def get_coop_user(email: str):
    try:
        return await cooperative_db_handler.get_coop_user(email=email)
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("Account not found")
        raise e
    
async def get_coop_user_by_id(coop_user_id: UUID):
    try:
        return await cooperative_db_handler.get_coop_user_by_id(coop_user_id=coop_user_id)
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("user not found")
        raise e

async def coop_user_sign_up(user_in: schemas.CooperativeUser):
    try:
        await get_coop_user(email=user_in.email)
        raise TheocraftBadRequestException(
            message="Email exist for user"
        )
    except NotFound:
        user_in.password = auth_utils.hash_password(plain_password=user_in.password)
        user_profile = await cooperative_db_handler.create_coop_user(user=user_in)
        user_profile_dict = {"id": str(user_profile.id)}
        access_token, refresh_token = (
            dep.create_access_token(data=user_profile_dict),
            dep.create_refresh_token(data=user_profile_dict),
        )
        return user_schemas.UserAccessToken(
            access_token=access_token, refresh_token=refresh_token
        )

async def coop_user_login(password: str, email: str):
    user_profile = await get_coop_user(email=email)
    if not auth_utils.verify_password(
        hashed_password=user_profile.password, plain_password=password
    ):
        raise TheocraftAuthException(message="email or password is incorrect")
    payload_dict = {"id": str(user_profile.id)}
    access_token, refresh_token = dep.create_access_token(
        data=payload_dict
    ), dep.create_refresh_token(data=payload_dict)
    return user_schemas.UserAccessToken(
        access_token=access_token, refresh_token=refresh_token
    )

async def coop_user_update(user_update: schemas.CooperativeUserUpdate, coop_user_id: UUID):
    try:
        user = await cooperative_db_handler.update_coop_user(
            coop_user_update=user_update, coop_user_id=coop_user_id
        )
        return user
    except UpdateError as e:
        LOGGER.exception(e)
        LOGGER.error("unexplainable update error")
        raise TheocraftBadRequestException(message="coop user update failed")

async def verify_mfa_token(code: str):
    mfa_token = await user_db_handler.get_mfa_token(code=code)
    if datetime.now() > mfa_token.code_expires_at:
        await user_db_handler.delete_mfa_token(id=mfa_token.id)
        code = toks_utils.token_gen()
        mfa_token = await user_db_handler.create_mfa_token(
            email=mfa_token.email, code=code
        )
        await send_mail(
            subject="MFA Token for Cooperative Admin",
            reciepients=[mfa_token.email],
            payload={"token": mfa_token.code},
            template="user_auth/token_email_template.html",
        )
        raise TheocraftBadRequestException(message="verification code has expired")

    await user_db_handler.update_mfa_token(id=mfa_token.id, verified=True)
    return

async def reset_password(code: int, new_password: str) -> user_db_handler.User_DB:
    try:
        mfa_token_read = await user_db_handler.get_mfa_token(code=code)
        await verify_mfa_token(code=mfa_token_read.code)
        user_profile = await get_coop_user(email=mfa_token_read.email)
        new_password = auth_utils.hash_password(plain_password=new_password)
        updated_user_profile = await coop_user_update(
            user_update=schemas.CooperativeUserUpdate(password=new_password),
            coop_user_id=user_profile.id,
        )
        return updated_user_profile
    except NotFound:
        LOGGER.error(f"forgot password token: {code} not valid")
        raise TheocraftNotFoundException(
            message=f"forgot password token: {code} not valid"
        )

async def forgot_password(email: str):
    await get_coop_user(email=email)
    # Create a Token 4 OTP
    code = toks_utils.token_gen()
    mfa_code_read = await user_db_handler.create_mfa_token(
        code=code, email=email
    )
    # send mail
    await send_mail(
        subject="Forgot Password",
        reciepients=[email],
        payload={"token": mfa_code_read.code},
        template="user_auth/token_email_template.html",
    )
    return {"messge": "otp sent"}

# ------- END OF COOP USER AUTH -------

# ------- START OF COOPERATIVE MANAGEMENT -------
async def create_cooperative(user_in: schemas.Cooperative, created_by: UUID):
    coop_id = f"COOP-{ShortUUID().random(length=10)}"
    return await cooperative_db_handler.create_cooperative(user=user_in, created_by=created_by, coop_id=coop_id)

async def get_cooperative(id: UUID):
    try:
        return await cooperative_db_handler.get_cooperative(id=id)
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("Cooperative not found")
        raise e

async def update_cooperative(coop_update: schemas.CooperativeProfileUpdate, id: UUID):
    try:
        coop_update = await cooperative_db_handler.update_cooperative(
            cooperative_details=coop_update, id=id
        )
        return coop_update
    except UpdateError as e:
        LOGGER.exception(e)
        LOGGER.error("Unexplainable cooperative profile update error")
        raise TheocraftBadRequestException(message="cooperative profile update failed")

# ------- END OF COOPERATIVE MANAGEMENT -------

# ------- START OF COOP MEMBER MANAGEMENT -------
async def get_coop_member(member_id: UUID, cooperative_id: UUID):
    try:
        return await cooperative_db_handler.get_coop_member(id=member_id, cooperative_id=cooperative_id)
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("Member Not found")
        raise e
    
async def get_all_coop_members(cooperative_id: UUID, status_filter: Optional[schemas.MembershipStatus] = None, page: int = 1, page_size: int = 20) -> schemas.PaginatedMembersResponse:
    try:
        members_data = await cooperative_db_handler.get_all_members(id=cooperative_id, status_filter=status_filter, page=page, page_size=page_size)
        total_pages = math.ceil(members_data["total_count"] / page_size)
        
        return schemas.PaginatedMembersResponse(
            members=members_data["members"],
            total_count=members_data["total_count"],
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("No member(s) found")
        raise e

async def update_coop_membership(member_update: schemas.MembershipUpdate):
    try:
        coop_member_update = await cooperative_db_handler.update_coop_membership(
            coop_member_update=member_update, coop_member_id=member_update.id, coop_id=member_update.cooperative_id
        )
        return coop_member_update
    except UpdateError as e:
        LOGGER.exception(e)
        LOGGER.error("Unexplainable cooperative member profile update error")
        raise TheocraftBadRequestException(message="cooperative member profile update failed")

async def change_coop_membership_status(member_update: schemas.MembershipUpdate):
    # change the membership status 
    # set the date_joined
    pass
# ------- END OF COOP MEMBER MANAGEMENT -------