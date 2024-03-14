from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from mmisp.util.uuid import uuid

from ..database import Base


class SharingGroup(Base):
    __tablename__ = "sharing_groups"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    releasability = Column(Text, nullable=False)
    description = Column(Text, nullable=False, default="")
    uuid = Column(String(40), unique=True, default=uuid, nullable=False)
    organisation_uuid = Column(String(40), nullable=False)
    org_id = Column(Integer, nullable=False, index=True)
    sync_user_id = Column(Integer, nullable=False, default=0, index=True)
    active = Column(Boolean, nullable=False, default=False)
    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    local = Column(Boolean, nullable=False, default=True)
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
    sharing_group_id = Column(Integer, index=True, nullable=False)
    server_id = Column(Integer, index=True, nullable=False)
    all_orgs = Column(Boolean, index=True, nullable=False, default=False)
