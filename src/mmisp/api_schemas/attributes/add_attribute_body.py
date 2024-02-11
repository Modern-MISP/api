from typing import Any, Optional

from pydantic import BaseModel, root_validator


class AddAttributeBody(BaseModel):
    type: str
    value: Optional[str]
    value1: Optional[str]
    value2: str | None = None
    event_id: str | None = None
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

    @root_validator
    def ensure_value_or_value1_is_set(cls, data: dict[str, Any]) -> Optional[dict[str, Any]]:  # noqa: ANN101
        required_values: list[str] = [str(data.get("value")), str(data.get("value1"))]
        if all(item is None for item in required_values):
            raise ValueError("value or value1 has to be set")
        return data

    class Config:
        orm_mode = True
