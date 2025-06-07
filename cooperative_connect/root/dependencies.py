import logging
from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer
from jose import ExpiredSignatureError, JWTError, jwt

import cooperative_connect.services.service_utils.gr_redis_utils as redis_utils
import cooperative_connect.services.user_service as admin_service
from cooperative_connect.database.orms.user_orm import User
from cooperative_connect.root.settings import Settings
from cooperative_connect.schemas.user_schemas import TokenData

LOGGER = logging.getLogger(__name__)

settings = Settings()
# AUTHENTICATION
bearer = HTTPBearer()
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 60 * 7
REFRESH_SECRET_KEY = settings.ref_jwt_secret_key
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 60 * 7 * 3


# TOP_LEVEL_SIGNER
ITS_DANGEROUS_TOKEN_KEY = settings.second_signer_key


token_signer = URLSafeTimedSerializer(secret_key=ITS_DANGEROUS_TOKEN_KEY)


def sign_token(jwt_token: str) -> str:
    return token_signer.dumps(obj=jwt_token)


def resolve_token(signed_token: str, max_age: int):
    try:
        return token_signer.loads(s=signed_token, max_age=max_age)
    except (BadTimeSignature, BadSignature) as e:
        LOGGER.exception(e)
        raise Exception


def create_access_token(data: dict):
    expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) + datetime.utcnow()
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=data, key=SECRET_KEY, algorithm=ALGORITHM)
    dangerous_access_token = sign_token(jwt_token=encoded_jwt)

    return dangerous_access_token


def create_refresh_token(data: dict):
    expire = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES) + datetime.utcnow()
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=data, key=REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    # add signed_token
    dangerous_refresh_token = sign_token(jwt_token=encoded_jwt)
    return dangerous_refresh_token


async def verify_access_token(token: str):
    cache_token = redis_utils.get_token_blacklist(token=token)
    if cache_token:
        raise HTTPException(detail="black-listed token", status_code=401)

    try:
        jwt_token = resolve_token(
            signed_token=token, max_age=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    except Exception:
        LOGGER.error("Access_token top level signer decrypt failed")
        raise credentials_exception()

    try:
        payload = jwt.decode(token=jwt_token, key=SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("admin_uid")
        if id is None:
            LOGGER.error(f"Decrypted JWT has not id in payload. {payload}")
            raise credentials_exception()

        token_data = TokenData(id=UUID(id))
    except (JWTError, ExpiredSignatureError) as e:
        LOGGER.exception(e)
        LOGGER.error("JWT Decryption Error")
        raise credentials_exception()

    return token_data


async def verify_refresh_token(token: str):
    cache_token = redis_utils.get_token_blacklist(token=token)
    if cache_token:
        raise HTTPException(detail="black-listed token", status_code=401)
    try:
        jwt_token = resolve_token(
            signed_token=token, max_age=REFRESH_TOKEN_EXPIRE_MINUTES
        )

    except Exception:
        LOGGER.error("Access_token top level signer decrypt failed")
        raise credentials_exception()

    try:
        payload = jwt.decode(
            token=jwt_token, key=REFRESH_SECRET_KEY, algorithms=ALGORITHM
        )
        id: str = payload.get("admin_uid")
        if id is None:
            await redis_utils.delete_refresh_token(refresh_token=token)
            raise credentials_exception()

        token_data = TokenData(id=id)
    except (JWTError, ExpiredSignatureError) as e:
        LOGGER.exception(e)
        redis_utils.delete_refresh_token(refresh_token=token)
        raise credentials_exception()

    return token_data


async def get_new_access_token(token: str):
    token_data = await verify_refresh_token(token=token)
    token_dict = {
        "id": str(token_data.id),
    }
    return create_access_token(data=token_dict)


def credentials_exception():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    auth_credential: HTTPAuthorizationCredentials = Depends(bearer),
):
    if not auth_credential.credentials:
        credentials_exception()

    token = await verify_access_token(token=auth_credential.credentials)

    user = await admin_service.get_user(id=token.id)
    return user


Current_User = Annotated[User, Depends(get_current_user)]
