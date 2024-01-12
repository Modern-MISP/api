from sqlalchemy import Boolean, Column, String
from sqlalchemy import ForeignKey

from ..database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organisations.id"))  # owner org
    orgc_id = Column(String, ForeignKey("organisations.id"))  # creator org
    distribution = Column(String)
    uuid = Column(String)
    date = Column(String)
    published = Column(Boolean)
    analysis = Column(String)
    attribute_count = Column(String)
    timestamp = Column(String)
    sharing_group_id = Column(String)
    proposal_email_lock = Column(Boolean)
    locked = Column(Boolean)
    threat_level_id = Column(String)
    publish_timestamp = Column(String)
    sighting_timestamp = Column(String)
    disable_correlation = Column(Boolean)
    extends_uuid = Column(String)
    event_creator_email = Column(String)
    protected = Column(Boolean)
    cryprographicKey: Column(list[str])


class EventReport(Base):
    __tablename__ = "event_report"

    id = Column(String, primary_key=True)
    uuid = Column(String)
    event_id = Column(String, ForeignKey("events.id"))
    name = Column(String)
    content = Column(String)
    distribution = Column(String)
    sharing_group_id = Column(String, ForeignKey("sharing_groups.id"))
    timestamp = Column(String)
    deleted = Column(Boolean)
