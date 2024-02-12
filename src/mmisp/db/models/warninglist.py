from sqlalchemy import Boolean, Column, Integer, String

from ..database import Base


class Warninglist(Base):
    __tablename__ = "warninglists"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    type = Column(String(255))
    description = Column(String(255))
    version = Column(Integer, default=1)
    enabled = Column(Boolean, default=True)
    default = Column(Boolean)
    category = Column(String(255))
    warninglist_entry_count = Column(Integer)
    valid_attributes = Column(String(255))
    # warninglistEntry = relationship("WarninglistEntries")


class WarninglistEntry(Base):
    __tablename__ = "warninglist_entries"
    id = Column(Integer, primary_key=True)
    value = Column(String(255))
    warninglist_id = Column(String(255))
    comment = Column(String(255), nullable=True)
