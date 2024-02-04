from pydantic import BaseModel


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
    numerical_value: int
    is_galaxy: bool
    is_costum_galaxy: bool
    local_only: bool
    local: int
    relationship_type: str


class AddEditGetEventAttributes(BaseModel):
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
    protected: bool
    event_creator_email: str
    Org: AddEditGetEventOrg
    Orgc: AddEditGetEventOrg
    Attribute: list[str]
    ShadowAttribute: list[AddEditGetEventShadowAttribute]
    RelatedEvent: list[str]
    Galaxy: list[str]
    Object: list[str]
    EventReport: list[AddEditGetEventEventReport]
    CryptographicKey: list[str]
    Tag: list[AddEditGetEventTag]


class AddEditGetEventResponse(BaseModel):
    Event: AddEditGetEventAttributes

    class Config:
        orm_mode = True
