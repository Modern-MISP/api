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


class ObjectWithAttributesSearchResponse(BaseModel):
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


class ObjectResponse(BaseModel):
    object: ObjectWithAttributesSearchResponse


class ObjectSearchResponse(BaseModel):
    response: list[ObjectResponse]

    class Config:
        orm_mode = True
