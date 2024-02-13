from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from mmisp.util.uuid import uuid

from ..database import Base
from .organisation import Organisation
from .tag import Tag


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid, index=True)
    org_id = Column(Integer, ForeignKey(Organisation.id), nullable=False, index=True)  # owner org
    orgc_id = Column(Integer, ForeignKey(Organisation.id), nullable=False, index=True)  # creator org
    info = Column(String(255), nullable=False, index=True)
    distribution = Column(String(255), nullable=False, default="0")
    date = Column(String(255), nullable=False)
    published = Column(Boolean, nullable=False, default=False)
    analysis = Column(String(255), nullable=False)
    attribute_count = Column(Integer, default=0)
    timestamp = Column(Integer, nullable=False, default=0)
    sharing_group_id = Column(String(255), nullable=True, default=None, index=True)
    proposal_email_lock = Column(Boolean, nullable=False, default=False)
    locked = Column(Boolean, nullable=False, default=False)
    threat_level_id = Column(Integer, nullable=False)
    publish_timestamp = Column(String(255), nullable=False, default=0)
    sighting_timestamp = Column(String(255), nullable=False, default=0)
    disable_correlation = Column(Boolean, nullable=False, default=False)
    extends_uuid = Column(String(255), default="")
    event_creator_email = Column(String(255), nullable=False)
    protected = Column(Boolean, nullable=True, default=None)
    cryptographic_key = Column(String(255), nullable=True, default=None)  # must be serialized
    attributes = relationship("Attribute", back_populates="event")


class EventReport(Base):
    __tablename__ = "event_reports"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid)
    event_id = Column(Integer, ForeignKey(Event.id), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    content = Column(String(255), nullable=False, default="")


class EventTag(Base):
    __tablename__ = "event_tags"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey(Event.id), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey(Tag.id), nullable=False, index=True)
    local = Column(Boolean, nullable=False, default=False)
