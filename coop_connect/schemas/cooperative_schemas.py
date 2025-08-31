from datetime import date, datetime
from typing import Annotated, List, Optional
from uuid import UUID

from pydantic import AnyHttpUrl, EmailStr, Field, conint

from coop_connect.root.coop_enums import (
    CooperativeStatus,
    CooperativeUserRole,
    MembershipStatus,
    MembershipType,
)
from coop_connect.root.utils.base_schemas import (
    AbstractModel,
    CoopInt,
    PaginationModel,
    PhoneNumber,
)
from coop_connect.schemas.user_schemas import Address


class Cooperative(AbstractModel):
    name: str
    onboarding_requirements: Optional[dict] = None
    public_listing: bool = False
    bye_laws: Optional[str] = None


class CooperativeIn(Cooperative):
    creator_role: CooperativeUserRole


class CooperativeExtended(Cooperative):
    meta: dict = {}
    coop_id: str
    status: CooperativeStatus
    created_by: UUID


class CooperativeProfile(CooperativeExtended):
    id: UUID
    date_created_utc: datetime
    date_updated_utc: Optional[datetime] = None


class PaginatedCooperativeProfile(AbstractModel):
    result_set: list[CooperativeProfile] = []
    result_count: int = 0
    page: int = 0
    page_size: int = 0
    total_count: int = 0


class CooperativeUpdate(AbstractModel):
    name: Optional[str] = None
    public_listing: Optional[bool] = None
    onboarding_requirements: Optional[dict] = None
    meta: Optional[dict] = None


class EmergencyContact(AbstractModel):
    name: str
    relationship: str
    phone_number: PhoneNumber
    email: Optional[EmailStr] = None
    address: Optional[Address] = None


class Guarantor(AbstractModel):
    name: str
    phone_number: PhoneNumber
    email: Optional[EmailStr] = None
    address: Optional[Address] = None


class MembershipIn(AbstractModel):
    membership_type: MembershipType = MembershipType.REGULAR
    emergency_contact: Optional[list[EmergencyContact]] = None
    referrer: Optional[UUID] = None
    guarantors: Optional[list[Guarantor]] = None


class MembershipExtended(MembershipIn):
    membership_id: Optional[str] = None
    user_bio: UUID
    user_id: UUID
    status: MembershipStatus = MembershipStatus.PENDING_APPROVAL
    cooperative_id: UUID
    referal_code: str
    meta: Optional[dict] = None
    role: CooperativeUserRole


class MembershipProfile(MembershipExtended):
    id: UUID
    date_joined: Optional[datetime] = None
    shares_owned: int
    total_deposits: int
    credit_score: int
    date_created_utc: datetime
    date_updated_utc: Optional[datetime] = None


class MembershipUpdate(AbstractModel):
    date_joined: Optional[datetime] = None
    status: Optional[MembershipStatus] = None
    shares_owned: Optional[int] = None
    total_deposits: Optional[int] = None
    credit_score: Optional[int] = None
    membership_type: Optional[MembershipType] = None
    emergency_contact: Optional[dict] = None
    referrer: Optional[UUID] = None
    guarantors: Optional[list[Guarantor]] = None
    meta: Optional[dict] = None


class PaginatedMembersResponse(AbstractModel):
    result_set: List[MembershipProfile] = []
    result_count: int = 0
    page: int = 0
    page_size: int = 0
    total_count: int = 0


class PaginationCoopQuery(AbstractModel):
    search: Optional[str] = None
    public_listing: Optional[bool] = None


class PaginationMembCoopQuery(AbstractModel):
    search: Optional[str] = None
    status: Optional[MembershipStatus] = None


Years = Annotated[int, conint(ge=2025)]
