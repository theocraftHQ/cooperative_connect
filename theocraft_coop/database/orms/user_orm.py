from datetime import datetime, timedelta

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from theocraft_coop.root.utils.abstract_base import AbstractBase


class User(AbstractBase):
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    phone_number = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=False)
    user_type = Column(String, nullable=False)
    dob = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)
    bio = relationship("UserBio", back_populates="user", uselist=False)


class UserBio(AbstractBase):
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    bvn = Column(String, nullable=True)
    identification = Column(String, nullable=True)
    address = Column(JSONB, default=False)
    passport = Column(String, nullable=True)
    signature = Column(String, nullable=False)
    user = relationship("User", back_populates="bio")


class MfaToken(AbstractBase):
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    code = Column(String, unique=True, nullable=False)
    verified = Column(Boolean, default=False)
    code_expires_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now() + timedelta(minutes=30),
    )
