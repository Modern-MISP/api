from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from mmisp.db.database import Base


class Warninglist(Base):
    __tablename__ = "warninglists"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False, default="string")
    description = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    enabled = Column(Boolean, default=False, nullable=False)
    default = Column(Boolean, default=True)
    category = Column(String(255))


class WarninglistEntry(Base):
    __tablename__ = "warninglist_entries"

    id = Column(Integer, primary_key=True, nullable=False)
    value = Column(String(255), nullable=False)
    warninglist_id = Column(Integer, ForeignKey(Warninglist.id, ondelete="CASCADE"), nullable=False)
    comment = Column(String(255))


class WarninglistType(Base):
    __tablename__ = "warninglist_types"

    id = Column(Integer, primary_key=True, nullable=False)
    type = Column(String(255), nullable=False)
    warninglist_id = Column(Integer, ForeignKey(Warninglist.id, ondelete="CASCADE"), nullable=False)
