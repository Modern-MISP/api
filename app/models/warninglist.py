from sqlalchemy import Boolean, Column, Integer, String

from ..database import Base


class WarninglistEntry(Base):
    __tablename__ = "warninglistEntry"
    id = Column(String)
    value = Column(String)
    warninglist_id = Column(String)
    comment = Column(String)


class Warninglist(Base):
    __tablename__ = "warninglist"
    id = Column(String, primary_key=True)
    name = Column(String)
    type = Column(String)
    description = Column(String)
    version = Column(String)
    enabled = Column(Boolean)
    category = Column(String)
    WarninglistEntry = Column(list[WarninglistEntry])
