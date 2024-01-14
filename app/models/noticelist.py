from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship

from ..database import Base


class Noticelist(Base):
    __tablename__ = "noticelists"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    expanded_name = Column(String)
    ref = Column(String)  # data must be serialized
    geographical_area = Column(String)  # data must be serialized
    version = Column(Integer)
    enabled = Column(TINYINT)
    noticelist_entries = relationship("noticelistsEntries")


class NoticelistEntry(Base):
    __tablename__ = "noticelists_entries"
    id = Column(Integer, primary_key=True)
    noticelist_id = Column(Integer, ForeignKey("noticelists.id"))
    data = Column(String)
