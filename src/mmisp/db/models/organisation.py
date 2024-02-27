from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from mmisp.util.uuid import uuid

from ..database import Base


class Organisation(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(255), unique=True, default=uuid)
    name = Column(String(255), nullable=False, unique=True)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    description = Column(String(255))
    type = Column(String(255))
    nationality = Column(String(255))
    sector = Column(String(255))
    created_by = Column(Integer, nullable=False, default=0)
    contacts = Column(String(255))
    local = Column(Boolean, nullable=False, default=False)
    restricted_to_domain = Column(String(255))
    landingpage = Column(String(255))
