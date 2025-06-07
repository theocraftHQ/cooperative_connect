from sqlalchemy import Column, String

from cooperative_connect.root.utils.abstract_base import AbstractBase


class User(AbstractBase):
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    phone_number = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=False)
    user_type = Column(String, nullable=False)
