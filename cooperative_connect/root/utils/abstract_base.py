import re
from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


def resolve_table_name(name):
    """Resolves table names to their mapped names."""
    names = re.split("(?=[A-Z])", name)  # noqa
    return "_".join([x.lower() for x in names if x])


class AbstractBase(DeclarativeBase):
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    date_created_utc = Column(DateTime(), default=datetime.utcnow)
    date_updated_utc = Column(DateTime(), onupdate=datetime.utcnow)

    @declared_attr
    def __tablename__(self):
        return resolve_table_name(self.__name__)

    @declared_attr
    def meta(cls):
        """Add metadata column to all models inheriting from CustomBase."""
        return Column(JSON, nullable=True, default=dict)

    def as_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}
