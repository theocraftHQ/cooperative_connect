from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from theocraft_coop.root.connect_enums import Gender, UploadPurpose, UserType
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


class Address(AbstractModel):
    street: str
    city: str
    state: str
    country: str
    postal_code: Optional[str] = None


class UserBio(AbstractModel):
    bvn: Optional[str] = None
    identification: Optional[UUID] = None
    address: Optional[Address] = None
    passport: Optional[UUID] = None
    signature: Optional[UUID] = None


class FileLite(AbstractModel):
    id: UUID
    purpose: UploadPurpose
    file_name: str
    link: str


class UserBioRead(UserBio):
    identification_file: Optional[FileLite] = None
    passport_file: Optional[FileLite] = None
    signature_file: Optional[FileLite] = None


class UserOnboard(User):
    user_bio: Optional[UserBio] = None


class UserProfile(User):
    id: UUID
    bio: Optional[UserBioRead] = None
    date_created_utc: datetime
    date_updated_utc: Optional[datetime] = None
    # excluding password
    password: str = Field(exclude=True)
    email: Optional[EmailStr] = Field(exclude=True, default=None)


class UserUpdate(AbstractModel):
    # TODO: Use a smarter method to make all fields optional
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[Gender] = None
    user_bio: Optional[UserBio] = None


class TokenData(AbstractModel):
    id: UUID


class UserAccessToken(AbstractModel):
    access_token: str
    refresh_token: str
