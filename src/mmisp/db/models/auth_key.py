from time import time

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from mmisp.util.uuid import uuid

from ..database import Base
from .user import User


class AuthKey(Base):
    __tablename__ = "auth_keys"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(255), unique=True, default=uuid, nullable=False)
    authkey = Column(String(255), nullable=False)
    authkey_start = Column(String(4), nullable=False)
    authkey_end = Column(String(4), nullable=False)
    created = Column(Integer, nullable=False, default=time)
    expiration = Column(Integer, nullable=False, default=0)
    read_only = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    comment = Column(Text)
    allowed_ips = Column(Text)
    unique_ips = Column(Text)

    user = relationship(User, primaryjoin=user_id == User.id)
