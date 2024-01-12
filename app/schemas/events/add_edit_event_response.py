from pydantic import BaseModel
from .get_event_response import GetEventOrg


class AddEditEventAttributes(BaseModel):
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
    Org: GetEventOrg
    Orgc: GetEventOrg
    Attribute: list[str]
    ShadowAttribute: list[str]
    RelatedEvent: list[str]
    Galaxy: list[str]
    Object: list[str]
    EventReport: list[str]
    CryptographicKey: list[str]


class AddEditEventResponse(BaseModel):
    Event: AddEditEventAttributes

    class Config:
        orm_mode = True
