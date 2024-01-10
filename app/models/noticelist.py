from sqlalchemy import Boolean, Column, Integer, String

from ..database import Base


class Noticelist(Base):
    __tablename__ = "noticelist"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    expanded_name = Column(String)
    ref = Column(list[String])
    geographical_area = Column(list[String])
    version = Column(Integer)
    enabled = Column(Boolean)
