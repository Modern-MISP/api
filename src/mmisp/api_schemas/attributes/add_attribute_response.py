from typing import Annotated

from pydantic import BaseModel, Field


class AddAttributeResponse(BaseModel):
    id: str
    event_id: str
    object_id: str
    object_relation: str
    category: str
    type: str
    value: str
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
    attribute_tag: Annotated[list[str], Field(alias="AttributeTag")]  # new

    class Config:
        orm_mode = True
