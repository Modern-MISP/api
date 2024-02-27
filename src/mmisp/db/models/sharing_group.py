from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from mmisp.util.uuid import uuid

from ..database import Base


class SharingGroup(Base):
    __tablename__ = "sharing_groups"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(255), unique=True, default=uuid, nullable=False)
    name = Column(String(255), nullable=False)
    releasability = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    organisation_uuid = Column(String(255), nullable=False)
    org_id = Column(Integer, nullable=False)
    sync_user_id = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False)
    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    local = Column(Boolean, nullable=False)
    roaming = Column(Boolean, default=False, nullable=False)


class SharingGroupOrg(Base):
    __tablename__ = "sharing_group_orgs"

    id = Column(Integer, primary_key=True, nullable=False)
    sharing_group_id = Column(Integer, index=True, nullable=False)
    org_id = Column(Integer, index=True, nullable=False)
    extend = Column(Boolean, default=False, nullable=False)


class SharingGroupServer(Base):
    __tablename__ = "sharing_group_servers"

    id = Column(Integer, primary_key=True, nullable=False)
    sharing_group_id = Column(Integer, nullable=False)
    server_id = Column(Integer, index=True, nullable=False)
    all_orgs = Column(Boolean, default=False, index=True, nullable=False)
