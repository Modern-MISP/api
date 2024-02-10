from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from mmisp.util.uuid import uuid

from ..database import Base


class SharingGroup(Base):
    __tablename__ = "sharing_groups"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid)
    name = Column(String(255))
    releasability = Column(String(255))
    description = Column(String(255), default="")
    organisation_uuid = Column(String(255))
    org_id = Column(Integer)
    sync_user_id = Column(Integer)
    active = Column(Boolean, default=True)
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow)
    local = Column(Boolean, default=False)
    roaming = Column(Boolean, default=False)


class SharingGroupOrg(Base):
    __tablename__ = "sharing_group_orgs"

    id = Column(Integer, primary_key=True)
    sharing_group_id = Column(Integer)
    org_id = Column(Integer)
    extend = Column(Boolean, default=False)


class SharingGroupServer(Base):
    __tablename__ = "sharing_group_servers"

    id = Column(Integer, primary_key=True)
    sharing_group_id = Column(Integer)
    server_id = Column(Integer)
    all_orgs = Column(Boolean, default=False)
