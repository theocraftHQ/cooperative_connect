from datetime import date, datetime
from typing import Annotated, List, Optional
from uuid import UUID

from pydantic import EmailStr, Field, conint

from coop_connect.root.coop_enums import (
    CooperativeStatus,
    CooperativeUserRole,
    MembershipStatus,
    MembershipType,
)
from coop_connect.root.utils.base_schemas import AbstractModel, CoopInt, PaginationModel
from coop_connect.schemas.form_schemas import Form, FormResponse


class Cooperative(AbstractModel):
    name: str
    onboarding_requirements: Optional[Form] = {}
    meta: dict
    public_listing: bool = False


class CooperativeIn(Cooperative):
    creator_role: CooperativeUserRole


class CooperativeExtended(Cooperative):
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
    onboarding_requirements: Optional[Form] = None
    meta: Optional[dict] = None


class MembershipIn(AbstractModel):
    user_id: UUID
    membership_type: MembershipType = MembershipType.REGULAR
    emergency_contact: Optional[dict] = {}
    onboarding_response: FormResponse
    referrer: Optional[UUID] = None
    guarrantors: Optional[dict] = None
    meta: Optional[dict] = None
    role: CooperativeUserRole


class MembershipExtended(MembershipIn):
    membership_id: Optional[str] = None
    status: MembershipStatus = MembershipStatus.PENDING_APPROVAL
    cooperative_id: UUID


class MembershipProfile(MembershipExtended):
    id: UUID
    date_joined: Optional[datetime] = None
    onboarding_response: FormResponse
    shares_owned: int
    total_deposit: int
    credit_score: int
    date_created_utc: datetime
    date_updated_utc: Optional[datetime] = None


class MembershipUpdate(AbstractModel):
    date_joined: Optional[datetime] = None
    onboarding_response: Optional[FormResponse] = None
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
