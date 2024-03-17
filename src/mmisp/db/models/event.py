from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from mmisp.util.uuid import uuid

from ..database import Base
from .organisation import Organisation
from .tag import Tag
from .user import User


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(40), unique=True, default=uuid, nullable=False, index=True)
    org_id = Column(Integer, ForeignKey(Organisation.id), nullable=False, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    info = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    published = Column(Boolean, nullable=False, default=False)
    analysis = Column(Integer, nullable=False)
    attribute_count = Column(Integer, default=0)
    orgc_id = Column(Integer, ForeignKey(Organisation.id), nullable=False, index=True)
    timestamp = Column(Integer, nullable=False, default=0)
    distribution = Column(Integer, nullable=False, default=0)
    sharing_group_id = Column(Integer, nullable=False, index=True, default=0)
    proposal_email_lock = Column(Boolean, nullable=False, default=False)
    locked = Column(Boolean, nullable=False, default=False)
    threat_level_id = Column(Integer, nullable=False)
    publish_timestamp = Column(Integer, nullable=False, default=0)
    sighting_timestamp = Column(Integer, nullable=False, default=0)
    disable_correlation = Column(Boolean, nullable=False, default=False)
    extends_uuid = Column(String(40), default="", index=True)
    protected = Column(Boolean)

    attributes = relationship("Attribute", back_populates="event")


class EventReport(Base):
    __tablename__ = "event_reports"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(40), unique=True, nullable=False, default=uuid)
    event_id = Column(Integer, ForeignKey(Event.id), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    content = Column(Text)
    distribution = Column(Integer, nullable=False, default=0)
    sharing_group_id = Column(Integer)
    timestamp = Column(Integer, nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)


class EventTag(Base):
    __tablename__ = "event_tags"

    id = Column(Integer, primary_key=True, nullable=False)
    event_id = Column(Integer, ForeignKey(Event.id, ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey(Tag.id, ondelete="CASCADE"), nullable=False, index=True)
    local = Column(Boolean, nullable=False, default=False)
