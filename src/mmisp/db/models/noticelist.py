from sqlalchemy import JSON, Boolean, Column, Integer, String

from ..database import Base


class Noticelist(Base):
    __tablename__ = "noticelists"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    expanded_name = Column(String(255))
    ref = Column(JSON)  # data must be serialized as json
    geographical_area = Column(JSON)  # data must be serialized as json
    version = Column(Integer)
    enabled = Column(Boolean)


class NoticelistEntry(Base):
    __tablename__ = "noticelists_entries"
    id = Column(Integer, primary_key=True)
    noticelist_id = Column(Integer, nullable=False)
    scope = Column(JSON)  # data must be serialized as json
    field = Column(JSON)  # data must be serialized as json
    value = Column(JSON)  # data must be serialized as json
    tags = Column(JSON)  # data must be serialized as json
    message = Column(String(255))
