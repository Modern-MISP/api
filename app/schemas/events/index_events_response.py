from pydantic import BaseModel
from .get_all_events_response import OrgResponse


class EventsAttributesResponse(BaseModel):
    id: str
    org_id: str
    date: str
    info: str
    uuid: str
    published: bool
    analysis: str
    attribute_count: str
    orgc_id: str
    timestamp: str
    distribution: str
    sharing_group_id: str
    proposal_email_lock: bool
    locked: bool
    threat_level_id: str
    publish_timestamp: str
    sighting_timestamp: str
    disable_correlation: bool
    extends_uuid: str
    protected: bool
    Org: OrgResponse
    Orgc: OrgResponse
    GalaxyCluster: []
    EventTag: []


class EventsIndexResponse(BaseModel):
    events: list[EventsAttributesResponse]

    class Config:
        orm_mode: True
