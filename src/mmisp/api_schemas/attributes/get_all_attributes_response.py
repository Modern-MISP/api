from typing import Any, Dict, Optional

from pydantic import BaseModel, validator


class GetAllAttributesResponse(BaseModel):
    id: str
    event_id: str | None = None
    object_id: str | None = None
    object_relation: str | None = None
    category: str | None = None
    type: str
    value: str
    value1: str | None = None  # new
    value2: str | None = None  # new
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

    @validator("sharing_group_id", always=True)
    def check_sharing_group_id(cls, value: Any, values: Dict[str, Any]) -> Optional[int]:  # noqa: ANN101
        """
        If distribution equals 4, sharing_group_id will be shown.
        """
        distribution = values.get("distribution", None)
        if distribution == "4" and value is not None:
            return value
        return None

    @validator(
        "event_id",
        "object_id",
        "timestamp",
        "distribution",
        "sharing_group_id",
        "first_seen",
        "last_seen",
        pre=True,
        allow_reuse=True,
    )
    def convert_to_string(cls, value: Optional[str]) -> Optional[str]:  # noqa: ANN101
        return str(value) if value is not None else None

    class Config:
        orm_mode = True
