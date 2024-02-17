from enum import Enum

from sqlalchemy import Boolean, Column, Integer, String

from ..database import Base


class WarninglistType(Enum):
    CIDR = "cidr"
    HOSTNAME = "hostname"
    STRING = "string"
    SUBSTRING = "substring"
    REGEX = "regex"


class WarninglistCategory(Enum):
    FALSE_POSITIVE = "False positive"
    KNOWN_IDENTIFIER = "Known identifier"


class Warninglist(Base):
    __tablename__ = "warninglists"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    type = Column(String(255))
    description = Column(String(255))
    version = Column(Integer, nullable=False, default=1)
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
    warninglist_id = Column(Integer)
    comment = Column(String(255), nullable=True)
