from pydantic import BaseModel

from ..organisations.organisation import Organisation


class AddEditGetEventGalaxyClusterMeta(BaseModel):
    external_id: str | None = None
    refs: list[str] | None = None
    kill_chain: str | None = None


class AddEditGetEventGalaxyClusterRelationTag(BaseModel):
    id: str
    name: str
    colour: str
    exportable: bool
    org_id: str
    user_id: str
    hide_tag: bool
    numerical_value: str
    is_galaxy: bool
    is_custom_galaxy: bool
    local_only: bool


class AddEditGetEventGalaxyClusterRelation(BaseModel):
    id: str
    galaxy_cluster_id: str
    referenced_galaxy_cluster_id: str
    referenced_galaxy_cluster_uuid: str
    referenced_galaxy_cluster_type: str
    galaxy_cluster_uuid: str
    distribution: str
    sharing_group_id: str | None = None
    default: bool
    Tag: list[AddEditGetEventGalaxyClusterRelationTag] = []


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
    distribution: str | None = None
    sharing_group_id: str | None = None
    org_id: str
    orgc_id: str
    default: bool | None = None
    locked: bool | None = None
    extends_uuid: str | None = None
    extends_version: str | None = None
    published: bool | None = None
    deleted: bool | None = None
    GalaxyClusterRelation: list[AddEditGetEventGalaxyClusterRelation] = []
    Org: Organisation | None = None
    Orgc: Organisation | None = None
    meta: AddEditGetEventGalaxyClusterMeta | None = None
    tag_id: str
    attribute_tag_id: str | None = None
    event_tag_id: str | None = None
    local: bool | None = None
    relationship_type: str = ""


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
    kill_chain_order: str | None = None
    GalaxyCluster: list[AddEditGetEventGalaxyCluster] = []


class AddEditGetEventOrg(BaseModel):
    id: str
    name: str
    uuid: str
    local: bool | None = None


class AddEditGetEventShadowAttribute(BaseModel):
    value: str
    to_ids: bool
    type: str
    category: str


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
    Event: list[AddEditGetEventRelatedEventAttributes] = []


class AddEditGetEventTag(BaseModel):
    id: str
    name: str
    colour: str
    exportable: str
    user_id: str
    hide_tag: bool
    numerical_value: int | None = None
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
    comment: str | None = None
    deleted: bool
    disable_correlation: bool
    first_seen: str | None = None
    last_seen: str | None = None
    Galaxy: list[AddEditGetEventGalaxy] = []
    ShadowAttribute: list[str] = []
    Tag: list[AddEditGetEventTag] = []


class AddEditGetEventObject(BaseModel):
    id: str
    name: str
    meta_category: str
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
    Attribute: list[AddEditGetEventAttribute] = []


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
