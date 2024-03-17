from typing import Optional

from pydantic import BaseModel, Field


class GetAttributeTag(BaseModel):
    id: str
    name: str
    colour: str
    numerical_value: int | None = None
    is_galaxy: bool
    local: bool


class GetAttributeAttributes(BaseModel):
    id: str
    event_id: str
    object_id: str
    object_relation: Optional[str] = Field(..., nullable=True)
    category: str
    type: str
    value: str
    to_ids: bool
    uuid: str
    timestamp: str
    distribution: str
    sharing_group_id: str
    comment: str | None = None
    deleted: bool
    disable_correlation: bool
    first_seen: Optional[str] = Field(..., nullable=True)
    last_seen: Optional[str] = Field(..., nullable=True)
    event_uuid: str
    tag: list[GetAttributeTag] | None = None


class GetAttributeResponse(BaseModel):
    Attribute: GetAttributeAttributes

    class Config:
        orm_mode = True
