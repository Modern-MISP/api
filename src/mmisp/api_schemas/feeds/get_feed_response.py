from pydantic import BaseModel


class FeedAttributesResponse(BaseModel):
    id: str
    name: str
    provider: str
    url: str
    rules: str | None = None
    enabled: bool
    distribution: bool
    sharing_group_id: str | None = None
    tag_id: str | None = None
    default: bool | None = None
    source_format: str
    fixed_event: bool
    delta_merge: bool | None = None
    event_id: str | None = None
    publish: bool | None = None
    override_ids: bool | None = None
    settings: str | None = None
    input_source: str | None = None
    delete_local_file: bool | None = None
    lookup_visible: bool | None = None
    headers: str | None = None
    caching_enabled: bool | None = None
    force_to_ids: bool | None = None
    orgc_id: str | None = None
    cache_timestamp: str | None = None  # deprecated
    cached_elements: str | None = None  # new
    coverage_by_other_feeds: str | None = None  # new


class FeedResponse(BaseModel):
    feed: list[FeedAttributesResponse]

    class Config:
        orm_mode = True
