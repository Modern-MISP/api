from time import time

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from mmisp.util.uuid import uuid

from ..database import Base
from .user import User


class AuthKey(Base):
    __tablename__ = "auth_keys"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid)
    read_only = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    authkey = Column(String(255))
    authkey_start = Column(String(255))
    authkey_end = Column(String(255))
    created = Column(Integer, default=time)
    expiration = Column(Integer)
    comment = Column(Text)
    allowed_ips = Column(Text)
    unique_ips = Column(Text)

    user = relationship(User, primaryjoin=user_id == User.id)
