from pydantic import BaseModel


class EditAttributeTag(BaseModel):
    id: str
    name: str
    colour: str
    exportable: str
    user_id: str
    hide_tag: bool
    numerical_value: int
    is_galaxy: bool
    is_costum_galaxy: bool
    local_only: bool


class EditAttributeAttributes(BaseModel):
    id: str
    event_id: str
    object_id: str
    object_relation: str | None = None
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
    first_seen: str | None = None
    last_seen: str | None = None
    tag: list[EditAttributeTag]


class EditAttributeResponse(BaseModel):
    Attribute: EditAttributeAttributes

    class Config:
        orm_mode = True
