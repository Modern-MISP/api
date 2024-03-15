from pydantic import BaseModel

from .get_attribute_response import GetAttributeTag


class SearchAttributesEvent(BaseModel):
    id: str
    org_id: str
    distribution: str
    info: str
    orgc_id: str
    uuid: str


class SearchAttributesObject(BaseModel):
    id: str
    distribution: str
    sharing_group_id: str


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
    comment: str | None = None
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
