from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import TINYINT

from ..database import Base


class Warninglist(Base):
    __tablename__ = "warninglists"
    id = Column(String(255), primary_key=True)
    name = Column(String(255))
    type = Column(String(255))
    description = Column(String(255))
    version = Column(Integer)
    enabled = Column(TINYINT)
    category = Column(String(255))
    warninglist_entry_count = Column(Integer)
    # warninglistEntry = relationship("WarninglistEntries")


class WarninglistEntry(Base):
    __tablename__ = "warninglist_entries"
    id = Column(String(255), primary_key=True)
    value = Column(String(255))
    warninglist_id = Column(String(255), ForeignKey(Warninglist.id))
    comment = Column(String(255))
