from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from coop_connect.root.utils.abstract_base import AbstractBase


class Cooperative(AbstractBase):
    coop_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    onboarding_requirements = Column(
        JSONB, default=False, nullable=True
    )  # requirements to join the coorporative
    public_listing = Column(Boolean, server_default=str(False))

    created_by = Column(UUID, ForeignKey("user.id"), nullable=False)

    user = relationship("User", back_populates="cooperatives")


class Member(AbstractBase):
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    user_bio = Column(UUID, ForeignKey("user_bio.id"), nullable=False)
    cooperative_id = Column(UUID, ForeignKey("cooperative.id"), nullable=False)
    membership_id = Column(
        String, unique=True, nullable=True
    )  # THEO-2025-001 [NAME OF COOP, YEAR JOINED, NUMBER IN THE YEAR]
    role = Column(String, nullable=False)
    date_joined = Column(DateTime, nullable=True)
    status = Column(
        String, nullable=False
    )  # MEMBERSHIP STATUS ./coop_connect/coop_enums.py
    membership_type = Column(String, nullable=False)
    emergency_contact = Column(JSONB, default=False, nullable=False)
    guarrantors = Column(JSONB, default=False, nullable=False)
    referal_code = Column(
        String, nullable=False
    )  # figure out the method for generating code automatically and uniquely
    referrer = Column(
        UUID, ForeignKey("user.id"), nullable=False
    )  # Need to create a separate table for referral and referral_code
    shares_owned = Column(Numeric(1), nullable=False, default=0)
    total_deposits = Column(Numeric(15, 2), nullable=False, default=0)
    credit_score = Column(Integer, nullable=False, default=0)
    onboarding_response = Column(JSONB, default=False, nullable=False)
    user = relationship("User", foreign_keys=[user_id])
    bio = relationship("UserBio", back_populates="member", foreign_keys=[user_bio])
    cooperative = relationship("Cooperative", foreign_keys=[cooperative_id])
