from pydantic import BaseModel


class FeedSchema(BaseModel):
    id: str
    name: str
    provider: str
    url: str
    rules: str
    enabled: bool
    distribution: str
    sharing_group_id: str
    tag_id: str
    default: bool
    source_format: str
    fixed_event: bool
    delta_merge: bool
    event_id: str
    publish: bool
    override_ids: bool
    settings: str
    input_source: str
    delete_local_file: bool
    lookup_visible: bool
    headers: str
    caching_enabled: bool
    force_to_ids: bool
    orgc_id: str
    cache_timestamp: str

    class Config:
        orm_mode = True


class FeedViewSchema(BaseModel):
    id: str
    name: str
    provider: str
    url: str
    rules: str
    enabled: bool
    distribution: str
    sharing_group_id: str
    tag_id: str
    default: bool
    source_format: str
    fixed_event: bool
    delta_merge: bool
    event_id: str
    publish: bool
    override_ids: bool
    settings: str
    input_source: str
    delete_local_file: bool
    lookup_visible: bool
    headers: str
    caching_enabled: bool
    force_to_ids: bool
    orgc_id: str
    cache_timestamp: str  # omitted
    cached_elements: str  # new
    coverage_by_other_feeds: str  # new

    class Config:
        orm_mode = True


class FeedTogleSchema(BaseModel):
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True


class FeedCacheSchema(BaseModel):
    name: str
    message: str
    url: str
    saved: bool  # new
    success: bool  # new

    class Config:
        orm_mode = True


class FeedFetchSchema(BaseModel):
    result: str
