from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.mysql import TINYINT
from ..database import Base


class Feed(Base):
    __tablename__ = "sharing_groups"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    releasability = Column(String)
    description = Column(String)
    uuid = Column(String)
    organisation_uuid = Column(String)
    org_id = Column(Integer)
    sync_user_id = Column(Integer)
    active = Column(TINYINT)
    created = Column(DateTime)
    modified = Column(DateTime)
    local = Column(TINYINT)
    roaming = Column(TINYINT)
