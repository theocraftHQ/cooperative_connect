from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr, Field

from theocraft_coop.root.cooperative_enums import CooperativeStatus, CooperativeUserRole, MembershipStatus, MembershipType
from theocraft_coop.root.utils.base_schemas import AbstractModel, Password, PhoneNumber


class Password(AbstractModel):
    password: Password

class Login(Password):
    email: Optional[EmailStr] = None
    phone_number: Optional[PhoneNumber] = None

class CooperativeUser(Login):
    first_name: str
    last_name: str
    avatar: str
    meta: dict

class CooperativeUserProfile(CooperativeUser):
    id: UUID
    role: str
    date_created_utc: datetime
    date_updated_utc: Optional[datetime] = None
    # excluding password
    password: str = Field(exclude=True)
    email: Optional[EmailStr] = Field(exclude=True, default=None)

class CooperativeUserUpdate(AbstractModel):
    # TODO: Use a smarter method to make all fields optional
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    avatar: Optional[str] = None
    meta: Optional[dict] = None

class Cooperative(AbstractModel):
    name: str
    onboarding_requirements: dict
    meta: dict

class CooperativeProfile(Cooperative):
    id: UUID
    coop_id: str
    status: str
    date_created_utc: datetime
    date_updated_utc: Optional[datetime] = None

class CooperativeProfileUpdate(AbstractModel):
    name: Optional[str] = None
    onboarding_requirement: Optional[dict] = None
    meta: Optional[dict] = None

class Membership(AbstractModel):
    user_id: UUID
    cooperative_id: UUID
    membership_type: MembershipType = MembershipType.REGULAR
    emergency_contact: dict
    referrer: UUID
    guarrantors: dict
    meta: dict

class MembershipProfile(Membership):
    id: UUID
    membership_id: Optional[str] = None
    date_joined: Optional[datetime] = None
    shares_owned: int
    total_deposit: int
    credit_score: int
    date_created_utc: datetime
    date_updated_utc: Optional[datetime] = None

class MembershipUpdate(AbstractModel):
    date_joined: Optional[datetime] = None
    status: Optional[str] = None
    shares_owned: Optional[int] = None
    total_deposit: Optional[int] = None
    credit_score: Optional[int] = None
    membership_type: Optional[MembershipType] = None
    emergency_contact: Optional[dict] = None
    referrer: Optional[UUID] = None
    guarrantors: Optional[dict] = None
    meta: Optional[dict] = None

class PaginatedMembersResponse(AbstractModel):
    members: List[MembershipProfile]
    total_count: int
    page: int
    page_size: int
    total_pages: int