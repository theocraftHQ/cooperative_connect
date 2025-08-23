from theocraft_coop.root.utils.abstract_base import AbstractBase
from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship



class CooperativeUser(AbstractBase):
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    phone_number = Column(String(15), nullable=True, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    meta =  Column(JSONB, default=False, nullable=True)

    cooperative = relationship("Cooperative", back_populates="cooperative_user")

class Cooperative(AbstractBase):
    coop_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    onboarding_requirements = Column(JSONB, default=False, nullable=True) # requirements to join the coorporative
    meta = Column(JSONB, default=False, nullable=True) # stakeholder information and coorporative documents will be stored here
    created_by = Column(UUID, ForeignKey("cooperative_user.id"), nullable=False)
    
    cooperative_user = relationship("CooperativeUser", back_populates="cooperative")

class Member(AbstractBase):
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    cooperative_id = Column(UUID, ForeignKey("cooperative.id"), nullable=False)
    membership_id = Column(String, unique=True, nullable=True)
    date_joined = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)
    membership_type = Column(String, nullable=False)
    shares_owned = Column(String, nullable=False, default=0)
    total_deposits = Column(Numeric(15, 2), nullable=False, default=0)
    credit_score = Column(Integer, nullable=False, default=0)
    emergency_contact = Column(JSONB, default=False, nullable=False)
    guarrantors = Column(JSONB, default=False, nullable=False)
    # referrer = Column(UUID, ForeignKey("user.id"), nullable=False) # Need to create a separate table for referral and referral_code
    meta =  Column(JSONB, default=False, nullable=False) #onboarding data will be stored here, who created the account and who approved the account

    user = relationship("User")



