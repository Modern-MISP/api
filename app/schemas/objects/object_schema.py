from typing import List

from pydantic import BaseModel


class AttributeSchema(BaseModel):
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


class ObjectSchema(BaseModel):
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
    Attribute: List[AttributeSchema]

    class Config:
        orm_mode = True


class ResponseSchema(BaseModel):
    Object: ObjectSchema

    class Config:
        orm_mode = True


class ObjectDeleteSchema(BaseModel):
    saved: str
    success: str
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True
