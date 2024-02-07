from pydantic import BaseModel


class FeedAttributesResponse(BaseModel):
    id: str
    name: str
    provider: str
    url: str
    rules: str | None = None
    enabled: bool | None = None
    distribution: int
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


class FeedResponse(BaseModel):
    feed: list[FeedAttributesResponse]

    class Config:
        orm_mode = True
