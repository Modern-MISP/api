from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    password = Column(String(255), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False, default=0)
    email = Column(String(255), nullable=False, unique=True)
    autoalert = Column(Boolean, default=False, nullable=False)
    authkey = Column(String(255), nullable=True, default=None)
    invited_by = Column(Integer, default=0, nullable=False)
    gpgkey = Column(String(255))
    certif_public = Column(String(255))
    nids_sid = Column(Integer, default=0, nullable=False)
    termsaccepted = Column(Boolean, default=False)
    newsread = Column(Integer, unsigned=True, default=0)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, default=0)
    change_pw = Column(Integer, default=0, nullable=False)
    contactalert = Column(Boolean, default=False, nullable=False)
    disabled = Column(Boolean, default=False, nullable=False)
    expiration = Column(DateTime, default=None)
    current_login = Column(Integer, default=0)
    last_login = Column(Integer, default=0)
    force_logout = Column(Boolean, default=False, nullable=False)
    date_created = Column(Integer)
    date_modified = Column(Integer)
