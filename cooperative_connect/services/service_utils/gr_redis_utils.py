import json
from typing import Optional
from uuid import UUID

from cooperative_connect.root.redis_manager import cc_redis


def refresh_token_key_generator(key: str):
    return f"Refresh-Token-{key}"


def add_refresh_token(refresh_token: str, expire_time: int):
    key = refresh_token_key_generator(key=refresh_token)
    return cc_redis.set(name=key, value=refresh_token, ex=expire_time)


def get_refresh_token(refresh_token: str) -> Optional[str]:
    key = refresh_token_key_generator(key=refresh_token)
    return cc_redis.get(name=key)


def delete_refresh_token(refresh_token: str):
    key = refresh_token_key_generator(key=refresh_token)
    return cc_redis.delete(key)


FORGET_PASSWORD_EXPIRE = 120


def forget_key_generator(token: int):
    return f"Forget-Key-{token}"


def add_forget_token(token: int, email: str):
    key = forget_key_generator(token=token)

    return cc_redis.set(name=key, value=email, ex=FORGET_PASSWORD_EXPIRE)


def get_forget_token(token: int):
    key = forget_key_generator(token=token)

    return cc_redis.get(name=key)


def delete_forget_token(token: int):
    key = forget_key_generator(token=token)
    return cc_redis.delete(key)


def black_list_bearer_tokens(access_token: str):
    return f"black-list-token-{access_token}"


def add_token_blacklist(access_token: str, refresh_token: str):
    for token in [access_token, refresh_token]:
        key = black_list_bearer_tokens(access_token=token)
        cc_redis.set(name=key, value=token, ex=60 * 60 * 24)


def get_token_blacklist(token: str):
    key = black_list_bearer_tokens(access_token=token)
    return cc_redis.get(name=key)
