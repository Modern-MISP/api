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

    class Config:
        orm_mode = True


class AttributeRestSearchSchema(BaseModel):
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

    class Config:
        orm_mode = True


class AttributeAddSchema(BaseModel):
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
    attributeTag: List[str]  # new

    class Config:
        orm_mode = True


class AttributeEditSchema(BaseModel):
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
    event_uuid: str  # new

    class Config:
        orm_mode = True


class AttributeDeleteSchema(BaseModel):
    message: str

    class Config:
        orm_mode = True


class AttributeDeleteSelectedSchema(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str
    id: str

    class Config:
        orm_mode = True


class AttributeGetByIdSchema(BaseModel):
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
    event_uuid: str  # new
    attributeTag: List[str]  # new

    class Config:
        orm_mode = True


class AttributeFreeTextImport(BaseModel):
    comment: str
    value: str
    original_value: str
    to_ids: str
    type: str
    category: str
    distribution: str

    class Config:
        orm_mode = True


class AttributeTagSchema(BaseModel):
    saved: bool
    success: str
    check_publish: bool

    class Config:
        orm_mode = True


class ShadowAttribute(BaseModel):
    value: str
    to_ids: bool
    type: str
    category: str

    class Config:
        orm_mode = True
