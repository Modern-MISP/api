from pydantic import BaseModel


class SightingFiltersBody(BaseModel):
    value1: str | None = None
    value2: str | None = None
    type: str | None = None
    category: str | None = None
    from_: str | None = None  # 'from' is a reserved word in Python, so an underscore is added
    to: str | None = None
    last: str | None = None
    timestamp: str | None = None
    event_id: str | None = None
    uuid: str | None = None
    attribute_timestamp: str | None = None
    to_ids: bool | None = None
    deleted: bool | None = None
    event_timestamp: str | None = None
    event_info: str | None = None
    sharing_group: list[str] | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    requested_attributes: list[str]
    return_format: str | None = None
    limit: str | None = None


class SightingCreateBody(BaseModel):
    values: list[str]
    source: str | None = None
    timestamp: str | None = None
    filters: SightingFiltersBody | None = None

    class Config:
        orm_mode = True
