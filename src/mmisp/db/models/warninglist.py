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

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False, default="string")
    description = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    enabled = Column(Boolean, default=False, nullable=False)
    default = Column(Boolean)
    category = Column(String(255))


class WarninglistEntry(Base):
    __tablename__ = "warninglist_entries"

    id = Column(Integer, primary_key=True, nullable=False)
    value = Column(String(255), nullable=False)
    warninglist_id = Column(Integer, nullable=False)
    comment = Column(String(255), nullable=True)
