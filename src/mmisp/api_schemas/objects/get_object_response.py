from typing import Any, Dict, Optional

from pydantic import BaseModel, validator

from mmisp.api_schemas.attributes.get_all_attributes_response import GetAllAttributesResponse
from mmisp.api_schemas.events.get_event_response import ObjectEventResponse


class ObjectWithAttributesResponse(BaseModel):
    id: str
    uuid: str
    name: str
    meta_category: str | None = None
    description: str | None = None
    template_id: str | None = None
    template_uuid: str | None = None
    template_version: str
    event_id: str
    timestamp: str
    distribution: str
    sharing_group_id: str | None = None
    comment: str
    deleted: bool
    first_seen: str | None = None
    last_seen: str | None = None
    attributes: list[GetAllAttributesResponse]
    event: ObjectEventResponse | None = None

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
        "template_id",
        "template_version",
        "event_id",
        "timestamp",
        "sharing_group_id",
        "distribution",
        "sharing_group_id",
        "comment",
        "first_seen",
        "last_seen",
        pre=True,
        allow_reuse=True,
    )
    def convert_to_string(cls, value: Optional[str]) -> Optional[str]:  # noqa: ANN101
        return str(value) if value is not None else None


class ObjectResponse(BaseModel):
    object: ObjectWithAttributesResponse

    class Config:
        orm_mode = True


class ObjectSearchResponse(BaseModel):
    response: list[ObjectResponse]

    class Config:
        orm_mode = True
