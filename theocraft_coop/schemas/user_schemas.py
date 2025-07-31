from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from theocraft_coop.root.connect_enums import UserType
from theocraft_coop.root.utils.base_schemas import (
    AbstractModel,
    CoopInt,
    Password,
    PhoneNumber,
)


class PaginatedQuery(AbstractModel):
    limit: CoopInt = 10
    offset: CoopInt = 0


class Password(AbstractModel):
    password: Password


class Login(Password):
    email: Optional[EmailStr] = None
    phone_number: Optional[PhoneNumber] = None


class User(Login):
    first_name: str
    last_name: str
    user_type: UserType = UserType.coop_member


class UserBio(AbstractModel):
    bvn: Optional[str] = None
    identification: Optional[str] = None
    address: Optional[dict] = None
    passport: Optional[str] = None
    signature: Optional[str] = None


class UserOnboard(User):
    user_bio: Optional[UserBio] = None


class UserProfile(User):
    id: UUID
    bio: Optional[UserBio] = None
    date_created_utc: datetime
    date_updated_utc: Optional[datetime] = None
    # excluding password
    password: str = Field(exclude=True)
    email: EmailStr = Field(exclude=True)


class UserUpdate(AbstractModel):
    # TODO: Use a smarter method to make all fields optional
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: UserType
    phone_number: Optional[PhoneNumber] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class TokenData(AbstractModel):
    id: UUID


class UserAccessToken(AbstractModel):
    access_token: str
    refresh_token: str
