from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mysql import TINYINT

from mmisp.util.uuid import uuid

from ..database import Base


class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid)
    name = Column(String(255))
    date_created = Column(DateTime)
    date_modified = Column(DateTime)
    description = Column(String(255))
    type = Column(String(255))
    nationality = Column(String(255))
    sector = Column(String(255))
    created_by = Column(Integer)
    contacts = Column(String(255))
    local = Column(TINYINT)
    restricted_to_domain = Column(String(255))
    landingpage = Column(String(255))
