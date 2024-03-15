from pydantic import BaseModel

from .get_all_events_response import GetAllEventsGalaxyCluster, GetAllEventsOrg


class IndexEventsEventTag(BaseModel):
    id: str
    event_id: str
    tag_id: str
    local: bool


class IndexEventsAttributes(BaseModel):
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
    protected: bool | None = None
    Org: GetAllEventsOrg
    Orgc: GetAllEventsOrg
    GalaxyCluster: list[GetAllEventsGalaxyCluster] = []
    EventTag: list[IndexEventsEventTag] = []

    class Config:
        orm_mode = True
