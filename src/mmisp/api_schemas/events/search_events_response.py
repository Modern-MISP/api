from pydantic import BaseModel
from .add_edit_get_event_response import (
    AddEditGetEventOrg,
    AddEditGetEventEventReport,
    AddEditGetEventShadowAttribute,
)


class SearchEventsAttributes(BaseModel):
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
    Tag: list[str]


class SearchEventsResponse(BaseModel):
    response: list[SearchEventsAttributes]

    class Config:
        orm_mode = True
