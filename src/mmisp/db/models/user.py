from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mysql import BIGINT, TINYINT

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    password = Column(String(255))
    org_id = Column(Integer)
    server_id = Column(Integer)
    email = Column(String(255))
    autoalert = Column(TINYINT)
    authkey = Column(String(255))
    invited_by = Column(Integer)
    gpgkey = Column(String(255))
    certif_public = Column(String(255))
    nids_sid = Column(Integer)
    termsaccepted = Column(TINYINT)
    newsread = Column(Integer)
    role_id = Column(Integer)
    change_pw = Column(TINYINT)
    contactalert = Column(TINYINT)
    disabled = Column(TINYINT)
    expiration = Column(DateTime)
    current_login = Column(Integer)
    last_login = Column(Integer)
    force_logout = Column(TINYINT)
    date_created = Column(BIGINT)
    date_modified = Column(BIGINT)
    sub = Column(String(255))
    external_auth_required = Column(TINYINT)
    external_auth_key = Column(String(255))
    last_api_access = Column(Integer)
    notification_daily = Column(TINYINT)
    notification_weekly = Column(TINYINT)
    notification_monthly = Column(TINYINT)
    totp = Column(String(255))
    hotp_counter = Column(Integer)
    last_pw_change = Column(BIGINT)
