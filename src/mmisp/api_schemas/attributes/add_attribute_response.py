from typing import Optional

from pydantic import BaseModel, Field


class AddAttributeAttributes(BaseModel):
    id: str
    event_id: str
    object_id: str
    object_relation: Optional[str] = Field(..., nullable=True)
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
    first_seen: Optional[str] = Field(..., nullable=True)
    last_seen: Optional[str] = Field(..., nullable=True)
    attribute_tag: list[str] = Field([], alias="AttributeTag")


class AddAttributeResponse(BaseModel):
    Attribute: AddAttributeAttributes

    class Config:
        orm_mode = True
