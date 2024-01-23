from sqlalchemy import Boolean, Column, Integer, String

from ..database import Base


class AuthKey(Base):
    __tablename__ = "auth_keys"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255))
    read_only = Column(Boolean)
    user_id = Column(String(255))
    comment = Column(String(255))
    allowed_ips = Column(String(255))
    authkey_start = Column(String(255))
    authkey_end = Column(String(255))
    created = Column(String(255))
    expiration = Column(String(255))
    last_used = Column(String(255))
    unique_ips = Column(String(255))
