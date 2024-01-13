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
