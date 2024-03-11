from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from mmisp.db.database import Base


class Warninglist(Base):
    __tablename__ = "warninglists"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False, default="string")
    description = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    enabled = Column(Boolean, default=False, nullable=False)
    warninglist_entry_count = Column(Integer, nullable=False, default=0)
    default = Column(Boolean, nullable=False, default=True)
    category = Column(String(20), nullable=False, default="false_positive")


class WarninglistEntry(Base):
    __tablename__ = "warninglist_entries"

    id = Column(Integer, primary_key=True, nullable=False)
    value = Column(Text, nullable=False)
    warninglist_id = Column(Integer, ForeignKey(Warninglist.id, ondelete="CASCADE"), nullable=False)
    comment = Column(Text)


class WarninglistType(Base):
    __tablename__ = "warninglist_types"

    id = Column(Integer, primary_key=True, nullable=False)
    type = Column(String(255), nullable=False)
    warninglist_id = Column(Integer, ForeignKey(Warninglist.id, ondelete="CASCADE"), nullable=False)
