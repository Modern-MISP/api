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
    sharing_group_id: str
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
    cache_timestamp: str | None = None
    cached_elements: str | None = None  # new
    coverage_by_other_feeds: str | None = None  # new

    @validator("sharing_group_id", always=True)
    def check_sharing_group_id(cls, value: Any, values: Dict[str, Any]) -> Optional[int]:  # noqa: ANN101
        """
        If distribution equals 4, sharing_group_id will be shown.
        """
        distribution = values.get("distribution", None)
        if distribution == "4" and value is not None:
            return value
        return None

    @validator("distribution", "sharing_group_id", "tag_id", "event_id", "orgc_id", pre=True, allow_reuse=True)
    def convert_to_string(cls, value: Optional[str]) -> Optional[str]:  # noqa: ANN101
        return str(value) if value is not None else None


class FeedResponse(BaseModel):
    feed: FeedAttributesResponse

    class Config:
        orm_mode = True


class FeedsResponse(BaseModel):
    feeds: list[FeedAttributesResponse]

    class Config:
        orm_mode = True
