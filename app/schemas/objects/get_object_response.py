from pydantic import BaseModel


class ObjectAttributesResponse(BaseModel):
    id: str
    event_id: str
    object_id: str
    object_relation: str
    category: str
    type: str
    value: str  # deprecated
    value1: str  # new
    value2: str  # new
    attribute_tag: list[str]  # new
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


class ObjectEventResponse(BaseModel):
    id: str
    info: str
    org_id: str
    orgc_id: str


class ObjectWithAttributesAndEventSearchResponse(BaseModel):
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
    first_seen: str
    last_seen: str
    attributes: list[ObjectAttributesResponse]
    event: list[ObjectEventResponse]


class ObjectViewResponse(BaseModel):
    object: ObjectWithAttributesAndEventSearchResponse

    class Config:
        orm_mode = True
