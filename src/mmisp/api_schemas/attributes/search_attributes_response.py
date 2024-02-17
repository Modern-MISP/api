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
    # published: bool
    # analysis: str
    # attribute_count: str
    # timestamp: str
    # sharing_group_id: str
    # proposal_email_lock: bool
    # locked: bool
    # threat_level_id: str
    # publish_timestamp: str
    # sighting_timestamp: str
    # disable_correlation: bool
    # extends_uuid: str
    # event_creator_email: str
    # protected: str
    # cryptographic_key: Annotated[list[str], Field(alias="cryptographicKey")]


class SearchAttributesObject(BaseModel):
    id: str
    distribution: str
    sharing_group_id: str
    # event_id: str
    # object_id: str
    # object_relation: str
    # category: str
    # type: str
    # value: str
    # value1: str
    # value2: str
    # attribute_tag: list
    # to_ids: bool
    # uuid: str
    # timestamp: str
    # comment: str
    # deleted: bool
    # disable_correlation: bool
    # first_seen: str
    # last_seen: str


class SearchAttributesAttributesDetails(BaseModel):
    id: str
    event_id: str | None = None
    object_id: str | None = None
    object_relation: str | None = None
    category: str
    type: str
    value: str
    to_ids: bool
    uuid: str
    timestamp: str
    distribution: str
    sharing_group_id: str | None = None
    comment: str
    deleted: bool
    disable_correlation: bool
    first_seen: str | None = None
    last_seen: str | None = None
    Event: SearchAttributesEvent | None = None
    Object: SearchAttributesObject | None = None
    Tag: list[GetAttributeTag] = []


class SearchAttributesAttributes(BaseModel):
    Attribute: SearchAttributesAttributesDetails


class SearchAttributesResponse(BaseModel):
    response: list[SearchAttributesAttributes]

    class Config:
        orm_mode = True
