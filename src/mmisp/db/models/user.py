from time import time

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from ..database import Base
from .organisation import Organisation


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    password = Column(String(255), nullable=False)
    org_id = Column(Integer, ForeignKey(Organisation.id), nullable=False, index=True)
    server_id = Column(Integer, nullable=False, default=0, index=True)
    email = Column(String(255), nullable=False, unique=True)
    autoalert = Column(Boolean, default=False, nullable=False)
    authkey = Column(String(40), nullable=True, default=None)
    invited_by = Column(Integer, default=0, nullable=False)
    gpgkey = Column(Text)
    certif_public = Column(Text)
    nids_sid = Column(Integer, default=0, nullable=False)
    termsaccepted = Column(Boolean, default=False, nullable=False)
    newsread = Column(Integer, default=0)
    role_id = Column(Integer, nullable=False, default=0)
    change_pw = Column(Integer, default=0, nullable=False)
    contactalert = Column(Boolean, default=False, nullable=False)
    disabled = Column(Boolean, default=False, nullable=False)
    expiration = Column(DateTime, default=None)
    current_login = Column(Integer, default=0)
    last_login = Column(Integer, default=0)
    force_logout = Column(Boolean, default=False, nullable=False)
    date_created = Column(Integer, default=time)
    date_modified = Column(Integer, default=time, onupdate=time)
    sub = Column(String(255), unique=True)
    external_auth_required = Column(Boolean, nullable=False, default=False)
    external_auth_key = Column(Text)
    last_api_access = Column(Integer, default=0)
    notification_daily = Column(Boolean, nullable=False, default=False)
    notification_weekly = Column(Boolean, nullable=False, default=False)
    notification_monthly = Column(Boolean, nullable=False, default=False)
    totp = Column(String(255))
    hotp_counter = Column(Integer)
    last_pw_change = Column(BigInteger)
