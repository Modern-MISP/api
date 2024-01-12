from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Noticelist(Base):
    __tablename__ = "noticelists"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    expanded_name = Column(String)
    ref = Column(list[String])
    geographical_area = Column(list[String])
    version = Column(Integer)
    enabled = Column(Boolean)
    noticelist_entries = relationship("noticelistsEntries")


class NoticelistEntry(Base):
    __tablename__ = "noticelistsEntries"
    id = Column(Integer, primary_key=True)
    noticelist_id = Column(Integer, ForeignKey("noticelists.id"))
    data = Column(String)