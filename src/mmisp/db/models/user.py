from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    password = Column(String(255))
    org_id = Column(Integer)
    server_id = Column(Integer)
    email = Column(String(255))
    autoalert = Column(Boolean)
    authkey = Column(String(255))
    invited_by = Column(Integer)
    gpgkey = Column(String(255))
    certif_public = Column(String(255))
    nids_sid = Column(Integer)
    termsaccepted = Column(Boolean)
    newsread = Column(Integer)
    role_id = Column(Integer)
    change_pw = Column(Boolean)
    contactalert = Column(Boolean)
    disabled = Column(Boolean)
    expiration = Column(DateTime)  # TODO might need to add to api schema
    current_login = Column(Integer)
    last_login = Column(Integer)
    force_logout = Column(Boolean)
    date_created = Column(BigInteger)
    date_modified = Column(BigInteger)
    sub = Column(String(255))
    external_auth_required = Column(Boolean)
    external_auth_key = Column(String(255))
    last_api_access = Column(Integer)
    notification_daily = Column(Boolean)
    notification_weekly = Column(Boolean)
    notification_monthly = Column(Boolean)
    totp = Column(String(255))
    hotp_counter = Column(Integer)
    last_pw_change = Column(BigInteger)
