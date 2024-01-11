from pydantic import BaseModel


class OrgResponse(BaseModel):
    id: str
    name: str
    uuid: str


class GalaxyClusterMetaResponse(BaseModel):
    date: list[str]
    kill_chain: list[str]
    refs: list[str]


class GalaxyClusterGalaxyKillChainOrderResponse(BaseModel):
    example_of_threats: list[str]


class GalaxyClusterGalaxyResponse(BaseModel):
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
    kill_chain_order: GalaxyClusterGalaxyKillChainOrderResponse


class GalaxyClusterResponse(BaseModel):
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
    distribution: str
    sharing_group_id: str
    org_id: str
    orgc_id: str
    default: str
    locked: bool
    extends_uuid: str
    extends_version: str
    published: bool
    deleted: bool
    Galaxy: list[GalaxyClusterGalaxyResponse]
    tag_id: str
    local: bool
    relationship_type: str


class EventTagTagResponse(BaseModel):
    id: str
    name: str
    colour: str
    is_galaxy: bool


class EventTagResponse(BaseModel):
    id: str
    event_id: str
    tag_id: str
    local: bool
    relationship_type: str
    Tag: list[EventTagTagResponse]


class EventsAttributesResponse(BaseModel):
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
    protected: str
    Org: OrgResponse
    Orgc: OrgResponse
    GalaxyCluster: list[GalaxyClusterResponse]
    EventTag: list[EventTagResponse]


class EventsResponse(BaseModel):
    events: list[EventsAttributesResponse]

    class Config:
        orm_mode = True
