from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import TINYINT

from ..database import Base


class Noticelist(Base):
    __tablename__ = "noticelists"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    expanded_name = Column(String(255))
    ref = Column(String(255))  # data must be serialized
    geographical_area = Column(String(255))  # data must be serialized
    version = Column(Integer)
    enabled = Column(TINYINT)
    # noticelist_entries = relationship("noticelistsEntries")


class NoticelistEntry(Base):
    __tablename__ = "noticelists_entries"
    id = Column(Integer, primary_key=True)
    noticelist_id = Column(Integer, ForeignKey(Noticelist.id))
    data = Column(String(255))
