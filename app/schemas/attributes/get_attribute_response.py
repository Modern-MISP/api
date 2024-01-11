from pydantic import BaseModel


class AttributeTagResponse(BaseModel):
    id: str
    name: str
    colour: str
    numerical_value: int
    is_galaxy: bool
    local: bool

    class Config:
        orm_mode = True


class AttributeResponse(BaseModel):
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
    Tag: list[AttributeTagResponse]  # new

    class Config:
        orm_mode = True