from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from theocraft_coop.root.utils.abstract_base import AbstractBase


class File(AbstractBase):
    file_name = Column(String, nullable=False)
    purpose = Column(String, nullable=False)
    link = Column(String, nullable=False)
    link_expiration = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now() + timedelta(seconds=72000),
    )
    creator_id = Column(UUID, ForeignKey("user.id", ondelete="CASCADE"))
    creator = relationship("User")
