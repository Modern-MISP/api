from pydantic import BaseModel


class GetEventOrg(BaseModel):
    id: str
    name: str
    uuid: str
    local: bool


class GetEventShadowAttribute(BaseModel):
    value: str
    to_ids: bool
    type: str
    category: str


class GetEventEventReport(BaseModel):
    id: str
    uuid: str
    event_id: str
    name: str
    content: str
    distribution: str
    sharing_group_id: str
    timestamp: str
    deleted: bool


class GetEventResponse(BaseModel):
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
    event_creator_email: str
    protected: str
    ShadowAttribute: list[GetEventShadowAttribute]
    RelatedEvent: list[str]
    Galaxy: list[str]
    Object: list[str]
    EventResport: list[GetEventEventReport]
    CryptographicKey: list[str]
    Tag: list[str]

    class Config:
        orm_mode = True
