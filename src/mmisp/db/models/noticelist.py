from sqlalchemy import Boolean, Column, Integer, String, Text

from ..database import Base


class Noticelist(Base):
    __tablename__ = "noticelists"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    expanded_name = Column(String(255), nullable=False)
    ref = Column(String(255))  # data must be serialized as json
    geographical_area = Column(String(255), index=True)  # data must be serialized as json
    version = Column(Integer, nullable=False, default=1)
    enabled = Column(Boolean, nullable=False, default=False)


class NoticelistEntry(Base):
    __tablename__ = "noticelist_entries"
    id = Column(Integer, primary_key=True, nullable=False)
    noticelist_id = Column(Integer, nullable=False)
    scope = Column(Text)  # data must be serialized as json
    field = Column(Text)  # data must be serialized as json
    value = Column(Text)  # data must be serialized as json
    tags = Column(Text)  # data must be serialized as json
    message = Column(String(255))
    data = Column(String(255), nullable=False)
