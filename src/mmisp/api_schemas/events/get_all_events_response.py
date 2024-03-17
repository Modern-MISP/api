from pydantic import BaseModel

from .add_edit_get_event_response import AddEditGetEventGalaxyClusterMeta


class GetAllEventsOrg(BaseModel):
    id: str
    name: str
    uuid: str


class GetAllEventsGalaxyClusterGalaxy(BaseModel):
    id: str
    uuid: str
    name: str
    type: str
    description: str
    version: str
    icon: str
    namespace: str
    enabled: bool
    local_only: bool
    kill_chain_order: str | None = None


class GetAllEventsGalaxyCluster(BaseModel):
    id: str
    uuid: str
    collection_uuid: str
    type: str
    value: str
    tag_name: str
    description: str
    galaxy_id: str
    source: str
    authors: list[str]
    version: str
    distribution: str | None = None
    sharing_group_id: str | None = None
    org_id: str
    orgc_id: str
    default: str | None = None
    locked: bool | None = None
    extends_uuid: str
    extends_version: str
    published: bool | None = None
    deleted: bool | None = None
    Galaxy: GetAllEventsGalaxyClusterGalaxy
    meta: AddEditGetEventGalaxyClusterMeta | None = None
    tag_id: str
    local: bool | None = None
    relationship_type: str | None = None


class GetAllEventsEventTagTag(BaseModel):
    id: str
    name: str
    colour: str
    is_galaxy: bool


class GetAllEventsEventTag(BaseModel):
    id: str
    event_id: str
    tag_id: str
    local: bool
    relationship_type: str
    Tag: GetAllEventsEventTagTag


class GetAllEventsResponse(BaseModel):
    id: str
    org_id: str  # owner org
    distribution: str
    info: str
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
    event_creator_email: str  # omitted
    protected: str | None = None
    Org: GetAllEventsOrg
    Orgc: GetAllEventsOrg
    GalaxyCluster: list[GetAllEventsGalaxyCluster]
    EventTag: list[GetAllEventsEventTag]

    class Config:
        orm_mode = True
