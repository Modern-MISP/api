from pydantic import BaseModel


class EditAttributeBody(BaseModel):
    type: str | None = None
    value: str | None = None
    value1: str | None = None
    value2: str | None = None
    object_id: str | None = None
    object_relation: str | None = None
    category: str | None = None
    to_ids: bool | None = None
    uuid: str | None = None
    timestamp: str | None = None
    distribution: str | None = None
    sharing_group_id: str | None = None
    comment: str | None = None
    deleted: bool | None = None
    disable_correlation: bool | None = None
    first_seen: str | None = None
    last_seen: str | None = None

    class Config:
        orm_mode = True
