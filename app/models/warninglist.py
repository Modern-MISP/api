from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Warninglist(Base):
    __tablename__ = "warninglists"
    id = Column(String, primary_key=True)
    name = Column(String)
    type = Column(String)
    description = Column(String)
    version = Column(Integer)
    enabled = Column(Boolean)
    category = Column(String)
    warninglist_entry_count = Column(Integer)
    warninglistEntry = relationship("WarninglistEntries")


class WarninglistEntry(Base):
    __tablename__ = "warninglistEntries"
    id = Column(String, primary_key=True)
    value = Column(String)
    warninglist_id = Column(String, ForeignKey("warninglists.id"))
    comment = Column(String)
