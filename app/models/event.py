from typing import List

from sqlalchemy import Boolean, Column, String

from ..database import Base


class Event(Base):
    id = Column(String)
    org_id = Column(String)  # owner org
    distribution = Column(String)
    orgc_id = Column(String)  # creator org
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
    protected = Column(String)
    chryprographicKey: Column(List[str])


class EventReport(Base):
    id = Column(String)
    uuid = Column(String)
    event_id = Column(String)
    name = Column(String)
    content = Column(String)
    distribution = Column(String)
    sharing_group_id = Column(String)
    timestamp = Column(String)
    deleted = Column(Boolean)
