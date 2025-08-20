from theocraft_coop.root.utils.abstract_base import AbstractBase
from sqlalchemy import Column, String, Enum, ForeignKey, DateTime, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum


class CooperativeStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive" # They need to contact us or subscribe
    DEACTIVATED = "deactivated" # They no longer want to be with us

class CooperativeUserRole(enum.Enum):
    PRESIDENT = "president"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    ACCOUNTANT = "accountant"
    STAFF = "staff"

class Cooperative(AbstractBase):
    coop_id = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    status = Column(Enum(CooperativeStatus), default=CooperativeStatus.INACTIVE, nullable=False)
    onboarding_requirements = Column(JSONB, default=False, nullable=True)
    meta = Column(JSONB, default=False, nullable=True)
    cooperativeusers = relationship("CooperativeUser", back_populates="cooperative", uselist=True)


class CooperativeUser(AbstractBase):
    cooperative_id = Column(UUID, ForeignKey("cooperative.id"), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=True)
    phone_number = Column(String(15), nullable=True, unique=True)
    password = Column(String, nullable=False)
    role = Column(Enum(CooperativeUserRole), default=CooperativeUserRole.STAFF, nullable=False)
    avatar = Column(String, nullable=True)
    meta =  Column(JSONB, default=False, nullable=True)

    cooperative = relationship("Cooperative", back_populates="cooperativeusers")


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

    user = relationship("User")



