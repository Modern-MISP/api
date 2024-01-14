from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.mysql import TINYINT
from ..database import Base


class SharingGroup(Base):
    __tablename__ = "sharing_groups"

    id = Column(Integer, unique=True, primary_key=True)
    uuid = Column(String, unique=True)
    name = Column(String)
    releasability = Column(String)
    description = Column(String)
    organisation_uuid = Column(String)
    org_id = Column(Integer)
    sync_user_id = Column(Integer)
    active = Column(TINYINT)
    created = Column(DateTime)
    modified = Column(DateTime)
    local = Column(TINYINT)
    roaming = Column(TINYINT)


class SharingGroupOrg(Base):
    __tablename__ = "sharing_group_orgs"

    id = Column(Integer, primary_key=True)
    sharing_group_id = Column(Integer)
    org_id = Column(Integer)
    extend = Column(TINYINT)


class SharingGroupServer(Base):
    __tablename__ = "sharing_group_servers"

    id = Column(Integer, primary_key=True)
    sharing_group_id = Column(Integer)
    server_id = Column(Integer)
    all_orgs = Column(TINYINT)
