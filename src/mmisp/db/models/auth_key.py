from time import time

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from mmisp.util.uuid import uuid

from ..database import Base


class AuthKey(Base):
    __tablename__ = "auth_keys"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(255), unique=True, default=uuid, nullable=False)
    authkey = Column(String(255), nullable=False)
    authkey_start = Column(String(255), nullable=False)
    authkey_end = Column(String(255), nullable=False)
    created = Column(Integer, nullable=False, default=time)
    expiration = Column(Integer, nullable=False, default=0)
    read_only = Column(Boolean, nullable=False, default=0)
    comment = Column(String(255))
    allowed_ips = Column(String(255))
    unique_ips = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
