from pydantic import BaseModel, Field

from ..organisations.organisation import Organisation


class AddEditGetEventGalaxyClusterMeta(BaseModel):
    external_id: list[str]
    kill_chain: list[str]


class AddEditGetEventGalaxyCluster(BaseModel):
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
    sharing_group_id: str | None = None
    org_id: str
    orgc_id: str
    default: bool
    locked: bool
    extends_uuid: str
    extends_version: str
    published: bool
    deleted: bool
    GalaxyClusterRelation: list[str]
    Org: Organisation
    Orgc: Organisation
    meta: AddEditGetEventGalaxyClusterMeta
    tag_id: int
    event_tag_id: str
    local: bool
    relationship_type: bool


class AddEditGetEventGalaxy(BaseModel):
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
    kill_chain_order: str
    GalaxyCluster: list[AddEditGetEventGalaxyCluster]


class AddEditGetEventOrg(BaseModel):
    id: str
    name: str
    uuid: str
    local: bool


class AddEditGetEventShadowAttribute(BaseModel):
    value: str
    to_ids: bool
    type: str
    category: str


class AddEditGetEventAttributeTag(BaseModel):
    id: str
    name: str
    colour: str
    exportable: bool
    user_id: str
    hide_tag: bool
    numerical_value: str | None = None
    is_galaxy: bool
    is_custom_galaxy: bool
    local_only: bool
    local: int
    relationship_type: str | None = None


class AddEditGetEventAttribute(BaseModel):
    id: str
    event_id: str
    object_id: str
    object_relation: str | None = None
    category: str
    type: str
    value: str
    to_ids: bool
    uuid: str
    timestamp: str
    distribution: str
    sharing_group_id: str
    comment: str
    deleted: bool
    disable_correlation: bool
    first_seen: str | None = None
    last_seen: str | None = None
    Galaxy: list[str] = [AddEditGetEventGalaxy]
    ShadowAttribute: list[str] = []
    Tag: list[AddEditGetEventAttributeTag]


class AddEditGetEventRelatedEventAttributesOrg(BaseModel):
    id: str
    name: str
    uuid: str


class AddEditGetEventRelatedEventAttributes(BaseModel):
    id: str
    date: str
    threat_level_id: str
    info: str
    published: str
    uuid: str
    analysis: str
    timestamp: str
    distribution: str
    org_id: str
    orgc_id: str
    Org: AddEditGetEventRelatedEventAttributesOrg
    Orgc: AddEditGetEventRelatedEventAttributesOrg


class AddEditGetEventRelatedEvent(BaseModel):
    Event: AddEditGetEventRelatedEventAttributes


class AddEditGetEventObject(BaseModel):
    id: str
    name: str
    meta_category: str = Field(..., alias="meta-category")
    description: str
    template_uuid: str
    template_version: str
    event_id: str
    uuid: str
    timestamp: str
    distribution: str
    sharing_group_id: str
    comment: str
    deleted: bool
    first_seen: str | None = None
    last_seen: str | None = None
    ObjectReference: list[str] = []
    Attribute: str


class AddEditGetEventEventReport(BaseModel):
    id: str
    uuid: str
    event_id: str
    name: str
    content: str
    distribution: str
    sharing_group_id: str
    timestamp: str
    deleted: bool


class AddEditGetEventTag(BaseModel):
    id: str
    name: str
    colour: str
    exportable: str
    user_id: str
    hide_tag: bool
    numerical_value: int | None = None
    is_galaxy: bool
    is_costum_galaxy: bool
    local_only: bool
    local: int
    relationship_type: str | None = None


class AddEditGetEventDetails(BaseModel):
    id: str
    orgc_id: str
    org_id: str
    date: str
    threat_level_id: str
    info: str
    published: bool
    uuid: str
    attribute_count: str
    analysis: str
    timestamp: str
    distribution: str
    proposal_email_lock: bool
    locked: bool
    publish_timestamp: str
    sharing_group_id: str
    disable_correlation: bool
    extends_uuid: str
    protected: bool | None = None
    event_creator_email: str
    Org: AddEditGetEventOrg
    Orgc: AddEditGetEventOrg
    Attribute: list[AddEditGetEventAttribute] = []
    ShadowAttribute: list[AddEditGetEventShadowAttribute] = []
    RelatedEvent: list[AddEditGetEventEventReport] = []
    Galaxy: list[AddEditGetEventGalaxy] = []
    Object: list[AddEditGetEventObject] = []
    EventReport: list[AddEditGetEventEventReport] = []
    CryptographicKey: list[str] = []
    Tag: list[AddEditGetEventTag] = []


class AddEditGetEventResponse(BaseModel):
    Event: AddEditGetEventDetails

    class Config:
        orm_mode = True
