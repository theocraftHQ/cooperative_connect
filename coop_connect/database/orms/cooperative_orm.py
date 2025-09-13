from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship

from coop_connect.root.utils.abstract_base import AbstractBase


class Cooperative(AbstractBase):
    coop_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    acronym = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    onboarding_requirements = Column(
        ARRAY(JSONB), default=False, nullable=True
    )  # requirements to join the coorporative
    public_listing = Column(Boolean, server_default=str(False))
    bye_laws = Column(String, nullable=True)
    created_by = Column(UUID, ForeignKey("user.id"), nullable=False)
    is_approved = Column(Boolean, nullable=True)
    approved_by = Column(UUID, ForeignKey("user.id"), nullable=True)

    user = relationship(
        "User", back_populates="cooperatives", foreign_keys=[created_by]
    )


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
    emergency_contact = Column(
        MutableList.as_mutable(ARRAY(JSONB)), default=False, nullable=True
    )
    guarantors = Column(
        MutableList.as_mutable(ARRAY(JSONB)), default=False, nullable=True
    )
    referal_code = Column(
        String, nullable=True
    )  # figure out the method for generating code automatically and uniquely
    referrer = Column(
        UUID, ForeignKey("user.id"), nullable=True
    )  # Need to create a separate table for referral and referral_code
    shares_owned = Column(Numeric(1), nullable=False, default=0)
    total_deposits = Column(Numeric(15, 2), nullable=False, default=0)
    credit_score = Column(Integer, nullable=False, default=0)
    user = relationship("User", foreign_keys=[user_id])
    bio = relationship("UserBio", back_populates="member", foreign_keys=[user_bio])
    cooperative = relationship("Cooperative", foreign_keys=[cooperative_id])
    # figure out the method for generating code automatically and uniquely
    referrer = Column(
        UUID, ForeignKey("user.id"), nullable=True
    )  # Need to create a separate table for referral and referral_code
    shares_owned = Column(Numeric(1), nullable=False, default=0)
    total_deposits = Column(Numeric(15, 2), nullable=False, default=0)
    credit_score = Column(Integer, nullable=False, default=0)
    onboarding_response = Column(ARRAY(JSONB), default=False, nullable=True)
    user = relationship("User", foreign_keys=[user_id])
    bio = relationship("UserBio", back_populates="member", foreign_keys=[user_bio])
    cooperative = relationship("Cooperative", foreign_keys=[cooperative_id])


class Wallet(AbstractBase):
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    cooperative_id = Column(UUID, ForeignKey("cooperative.id"), nullable=False)
    balance = Column(String, default=0, nullable=False)
    currency_code = Column(String, nullable=False)
    precision = Column(Integer, default=2, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    user = relationship("User", foreign_keys=[user_id])
    cooperative = relationship("Cooperative", foreign_keys=[cooperative_id])


class ReservedBankAccount(AbstractBase):
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    cooperative_id = Column(UUID, ForeignKey("cooperative.id"), nullable=False)
    account_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    bank_code = Column(String, nullable=False)
    bank_name = Column(String, nullable=False)
    currency_code = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    account_reference = Column(String, nullable=False)
    status = Column(String, default="ACTIVE", nullable=False)
    user = relationship("User", foreign_keys=[user_id])
    cooperative = relationship("Cooperative", foreign_keys=[cooperative_id])


# class IncomingDeposits(AbstractBase):
#     user_id =
#     amount =
#     fee =
#     Total =
#     wallet_id =
#     status =
#     reference =
#     channel = # here it could be bank_transfer or cash
#     curenncy_code =


# class Fees:
# Cooperative can create different fees for members to pay, fees are usually statutory and compulsory
# cooperative_id
# name
# amount
# currency
# frequency: whether once, daily weekly monthly yearly
# is_mandatory
# goal oreinted: deduct based on percentage until it gets to a particular amount (i don't know how to structure this yet)

# I'm thinking of how we can separate money that can be given back to the users and the ones that can't be given back

# class Savings:
# type
# name
# amount
# currency
#


# class CoopConfig:
