from typing import List

from pydantic import BaseModel


class EventSchema(BaseModel):
    id: str
    org_id: str  # owner org
    distribution: str
    orgc_id: str  # creator org
    uuid: str
    date: str
    published: bool
    analysis: str
    attribute_count: str
    timestamp: str
    sharing_group_id: str
    proposal_email_lock: bool
    locked: bool
    threat_level_id: str
    publish_timestamp: str
    sighting_timestamp: str
    disable_correlation: bool
    extends_uuid: str
    event_creator_email: str
    protected: str
    chryprographicKey: List[str]

    class Config:
        orm_mode = True


class EventReportSchema(BaseModel):
    id: str
    uuid: str
    event_id: str
    name: str
    content: str
    distribution: str
    sharing_group_id: str
    timestamp: str
    deleted: bool

    class Config:
        orm_mode = True
