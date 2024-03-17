from typing import Any, Dict, Optional

from pydantic import BaseModel, validator


class FeedAttributesResponse(BaseModel):
    id: str
    name: str
    provider: str
    url: str
    rules: str | None = None
    enabled: bool | None = None
    distribution: str
    sharing_group_id: str | None = None
    tag_id: str
    default: bool | None = None
    source_format: str | None = None
    fixed_event: bool
    delta_merge: bool
    event_id: str
    publish: bool
    override_ids: bool
    settings: str | None = None
    input_source: str
    delete_local_file: bool | None = None
    lookup_visible: bool | None = None
    headers: str | None = None
    caching_enabled: bool
    force_to_ids: bool
    orgc_id: str

    @validator("sharing_group_id", always=True)
    def check_sharing_group_id(cls, value: Any, values: Dict[str, Any]) -> Optional[int]:  # noqa: ANN101
        """
        If distribution equals 4, sharing_group_id will be shown.
        """
        distribution = values.get("distribution", None)
        if distribution == "4" and value is not None:
            return value
        return None


class FeedResponse(BaseModel):
    Feed: FeedAttributesResponse

    class Config:
        orm_mode = True
