from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    password = Column(String)
    org_id = Column(Integer)
    sever_id = Column(Integer)
    email = Column(String)
    autoalert = Column(TINYINT)
    authkey = Column(String)
    invited_by = Column(Integer)
    gpgkey = Column(String)
    certif_public = Column(String)
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
    sub = Column(String)
    external_auth_required = Column(TINYINT)
    external_auth_key = Column(String)
    last_api_access = Column(Integer)
    notification_daily = Column(TINYINT)
    notification_weekly = Column(TINYINT)
    notification_monthly = Column(TINYINT)
    totp = Column(String)
    hotp_counter = Column(Integer)
    last_pw_change = Column(BIGINT)
