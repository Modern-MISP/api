from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class AuthKey(Base):
    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    read_only = Column(Boolean)
    user_id = Column(String)
    comment = Column(String)
    allowed_ips = Column(String)
    authkey_start = Column(String)
    authkey_end = Column(String)
    created = Column(String)
    expiration = Column(String)
    last_used = Column(String)
    unique_ips = Column(String)
    user = relationship("AuthKeyUser", backref="auth_key")


class AuthKeyUser(Base):
    id = Column(Integer, primary_key=True)
    org_id = Column(String)
