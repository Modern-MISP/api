from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from mmisp.db.database import Base


class Noticelist(Base):
    __tablename__ = "noticelists"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    expanded_name = Column(String(255), nullable=False)
    ref = Column(String(255))  # data serialized as json
    geographical_area = Column(String(255))  # data serialized as json
    version = Column(Integer, nullable=False, default=1)
    enabled = Column(Boolean, nullable=False, default=False)


class NoticelistEntry(Base):
    __tablename__ = "noticelist_entries"
    id = Column(Integer, primary_key=True, nullable=False)
    noticelist_id = Column(Integer, ForeignKey(Noticelist.id, ondelete="CASCADE"), nullable=False)
    data = Column(Text, nullable=False)  # data serialized as json
