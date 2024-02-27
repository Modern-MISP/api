from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from mmisp.util.uuid import uuid

from ..database import Base
from .user import User


class AuthKey(Base):
    __tablename__ = "auth_keys"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(255), unique=True, default=uuid)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    authkey = Column(String(255), nullable=False)
    authkey_start = Column(String(255), nullable=False)
    authkey_end = Column(String(255), nullable=False)
    created = Column(Integer, nullable=False)
    expiration = Column(Integer, nullable=False)
    comment = Column(String(255))
    allowed_ips = Column(String(255))
    unique_ips = Column(String(255))

    user = relationship(User, primaryjoin=user_id == User.id)
