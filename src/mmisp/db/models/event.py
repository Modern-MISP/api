from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from .organisation import Organisation
from .sharing_group import SharingGroup
from ..database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey(Organisation.id))  # owner org
    orgc_id = Column(Integer, ForeignKey(Organisation.id))  # creator org
    distribution = Column(String(255))
    uuid = Column(String(255), unique=True)
    date = Column(String(255))
    published = Column(Boolean)
    analysis = Column(String(255))
    attribute_count = Column(String(255))
    timestamp = Column(String(255))
    sharing_group_id = Column(String(255))
    proposal_email_lock = Column(Boolean)
    locked = Column(Boolean)
    threat_level_id = Column(String(255))
    publish_timestamp = Column(String(255))
    sighting_timestamp = Column(String(255))
    disable_correlation = Column(Boolean)
    extends_uuid = Column(String(255))
    event_creator_email = Column(String(255))
    protected = Column(Boolean)
    cryptographicKey = Column(String(255))  # must be serialized


class EventReport(Base):
    __tablename__ = "event_reports"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255))
    event_id = Column(Integer, ForeignKey(Event.id))
    name = Column(String(255))
    content = Column(String(255))
    distribution = Column(String(255))
    sharing_group_id = Column(Integer, ForeignKey(SharingGroup.id))
    timestamp = Column(String(255))
    deleted = Column(Boolean)
