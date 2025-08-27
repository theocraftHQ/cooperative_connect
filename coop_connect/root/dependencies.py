import logging
from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer
from jose import ExpiredSignatureError, JWTError, jwt

import coop_connect.services.cooperative_service as cooperative_service
import coop_connect.services.user_service as admin_service
from coop_connect.database.orms.cooperative_orm import CooperativeUser
from coop_connect.database.orms.user_orm import User
from coop_connect.root.settings import Settings
from coop_connect.schemas.user_schemas import TokenData

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

    try:
        jwt_token = resolve_token(
            signed_token=token, max_age=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    except Exception:
        LOGGER.error("Access_token top level signer decrypt failed")
        raise credentials_exception()

    try:
        payload = jwt.decode(token=jwt_token, key=SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("id")
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
        id: str = payload.get("id")
        if id is None:
            raise credentials_exception()

        token_data = TokenData(id=id)
    except (JWTError, ExpiredSignatureError) as e:
        LOGGER.exception(e)
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
    request: Request,
    auth_credential: HTTPAuthorizationCredentials = Depends(bearer),
):

    if getattr(request.state.user, None):
        return request.state.user

    if not auth_credential.credentials:
        credentials_exception()

    token = await verify_access_token(token=auth_credential.credentials)

    user = await admin_service.get_user(id=token.id)

    request.state.user = user
    return user


async def get_current_coop_user(
    auth_credential: HTTPAuthorizationCredentials = Depends(bearer),
):
    if not auth_credential.credentials:
        credentials_exception()

    token = await verify_access_token(token=auth_credential.credentials)

    # user = await cooperative_service.get_coop_user_by_id(coop_user_id=token.id)
    # return user


Current_User = Annotated[User, Depends(get_current_user)]
