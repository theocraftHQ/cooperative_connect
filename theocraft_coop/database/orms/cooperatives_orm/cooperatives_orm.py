from theocraft_coop.root.utils.abstract_base import AbstractBase
from sqlalchemy import Column, String, Enum, ForeignKey
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


class CooperativeUser(AbstractBase):
    cooperative_id = Column(UUID, ForeignKey("cooperative.id"), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=True)
    phone_number = Column(String(15), nullable=True, unique=True)
    password = Column(String, nullable=False)
    role = Column(Enum(CooperativeUserRole), default=CooperativeUserRole.VIEWER, nullable=False)
    avatar = Column(String, nullable=True)
    meta =  Column(JSONB, default=False, nullable=True)

    cooperative = relationship("Cooperative", backpopulate="cooperativeuser")