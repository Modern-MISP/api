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
    value1: str
    value2: str
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
    event_uuid: str
    attributeTag: List[str]

    class Config:
        orm_mode = True


class ShadowAttribute(BaseModel):
    value: str
    to_ids: bool
    type: str
    category: str

    class Config:
        orm_mode = True
