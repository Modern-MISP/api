from pydantic import BaseModel


class ObjectSearchBody(BaseModel):
    object_name: str | None = None
    object_template_uuid: str | None = None
    object_template_version: str | None = None
    event_id: str | None = None
    category: str | None = None
    comment: str | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    quick_filter: str | None = None
    timestamp: str | None = None
    event_info: str | None = None
    from_: str | None = None  # 'from' is a reserved word in Python, so an underscore is added
    to: str | None = None
    date: str | None = None
    last: str | None = None
    event_timestamp: str | None = None
    org_id: str | None = None
    uuid: str | None = None
    value: str | None = None
    value1: str | None = None  # new
    value2: str | None = None  # new
    type: str | None = None
    object_relation: str | None = None
    attribute_timestamp: str | None = None
    to_ids: bool | None = None
    published: bool | None = None
    deleted: bool | None = None
    return_format: str | None = "json"
    limit: str | None = None

    class Config:
        orm_mode = True
