from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mysql import TINYINT

from ..database import Base


class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    name = Column(String)
    date_created = Column(DateTime)
    date_modified = Column(DateTime)
    description = Column(String)
    type = Column(String)
    nationality = Column(String)
    sector = Column(String)
    created_by = Column(Integer)
    contacts = Column(String)
    local = Column(TINYINT)
    restricted_to_domain = Column(String)
    landingpage = Column(String)
