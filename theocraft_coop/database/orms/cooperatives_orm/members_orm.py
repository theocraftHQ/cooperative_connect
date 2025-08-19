from theocraft_coop.root.utils.abstract_base import AbstractBase
from sqlalchemy import Column, ForeignKey, String, DateTime, Enum, Numeric, Integer
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
import enum

class MembershipStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"

class MembershipType(str, enum.Enum):
    REGULAR = "regular"
    CORPORATE = "corporate"

class Member(AbstractBase):
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    cooperative_id = Column(UUID, ForeignKey("cooperative.id"), nullable=False)
    membership_id = Column(String(50), unique=True, nullable=True)
    date_joined = Column(DateTime, nullable=True)
    status = Column(Enum(MembershipStatus), default=MembershipStatus.PENDING, nullable=False)
    member_type = Column(Enum(MembershipType), nullable=False)
    shares_owned = Column(String(50), nullable=False, default=0)
    total_deposits = Column(Numeric(15, 2), nullable=False, default=0)
    credit_score = Column(Integer, nullable=False, default=0)
    emergency_contact = Column(JSONB, default=False, nullable=True)
    guarrantors = Column(JSONB, default=False, nullable=False)
    referrer = Column(UUID, ForeignKey("user.id"), nullable=False)
    meta =  Column(JSONB, default=False, nullable=False) #onboarding data will be stored here

    user = relationship("User", backpopulate="member")



