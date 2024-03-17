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
    template_uuid: str | None = None
    template_version: str | None = None
    event_id: str | None = None
    timestamp: str | None = None
    distribution: str | None = None
    sharing_group_id: str | None = None
    comment: str | None = None
    deleted: bool | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    Attribute: list[GetAllAttributesResponse] | None = None
    Event: ObjectEventResponse | None = None

    @validator("sharing_group_id", always=True)
    def check_sharing_group_id(cls, value: Any, values: Dict[str, Any]) -> Optional[int]:  # noqa: ANN101
        """
        If distribution equals 4, sharing_group_id will be shown.
        """
        distribution = values.get("distribution", None)
        if distribution == "4" and value is not None:
            return value
        return None


class ObjectResponse(BaseModel):
    Object: ObjectWithAttributesResponse

    class Config:
        orm_mode = True


class ObjectSearchResponse(BaseModel):
    response: list[ObjectResponse]

    class Config:
        orm_mode = True
