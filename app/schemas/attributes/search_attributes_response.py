from pydantic import BaseModel

from .get_attribute_response import GetAttributeTag


class SearchAttributesEvent(BaseModel):
    id: str
    org_id: str
    distribution: str
    info: str
    orgc_id: str
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
    chryprographicKey: list[str]


class SearchAttributesObject(BaseModel):
    id: str
    distribution: str
    sharing_group_id: str
    event_id: str
    object_id: str
    object_relation: str
    category: str
    type: str
    value: str
    value1: str
    value2: str
    attribute_tag: list
    to_ids: bool
    uuid: str
    timestamp: str
    comment: str
    deleted: bool
    disable_correlation: bool
    first_seen: str
    last_seen: str


class SearchAttributesResponse(BaseModel):
    id: str
    event_id: str
    object_id: str
    object_relation: str
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
    first_seen: str
    last_seen: str
    Event: SearchAttributesEvent
    Object: SearchAttributesObject
    Tag: list[GetAttributeTag]

    class Config:
        orm_mode = True
