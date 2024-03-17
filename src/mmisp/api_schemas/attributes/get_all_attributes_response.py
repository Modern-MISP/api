from typing import Any, Dict, Optional

from pydantic import BaseModel, validator


class GetAllAttributesResponse(BaseModel):
    id: str
    event_id: str | None = None
    object_id: str | None = None
    object_relation: str | None = None
    category: str | None = None
    type: str
    value1: str | None = None
    value2: str | None = None
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
    value: str | None = None

    @validator("sharing_group_id", always=True)
    def check_sharing_group_id(cls, value: Any, values: Dict[str, Any]) -> Optional[int]:  # noqa: ANN101
        """
        If distribution equals 4, sharing_group_id will be shown.
        """
        distribution = values.get("distribution", None)
        if distribution == "4" and value is not None:
            return value
        return None

    class Config:
        orm_mode = True
