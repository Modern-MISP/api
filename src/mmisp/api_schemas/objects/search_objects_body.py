from typing import Any

from pydantic import BaseModel, validator


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
    value1: str | None = None
    value2: str | None = None
    type: str | None = None
    object_relation: str | None = None
    attribute_timestamp: str | None = None
    to_ids: bool | None = None
    published: bool | None = None
    deleted: bool | None = None
    return_format: str | None = "json"
    limit: str | None = "25"

    @validator("limit")
    def check_limit(cls, value: Any) -> str:  # noqa: ANN101
        if value:
            try:
                limit_int = int(value)
            except ValueError:
                raise ValueError("'limit' must be a valid integer")

            if not 1 <= limit_int <= 500:
                raise ValueError("'limit' must be between 1 and 500")
        return value

    class Config:
        orm_mode = True
