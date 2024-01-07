from typing import Optional

from pydantic import BaseModel


class FeedSchema(BaseModel):
    id: str
    name: str
    provider: str
    url: str
    rules: Optional[str] = None
    enabled: bool
    distribution: Optional[str] = None
    sharing_group_id: Optional[str] = None
    tag_id: Optional[str] = None
    default: bool
    source_format: Optional[str] = None
    fixed_event: bool
    delta_merge: bool
    event_id: Optional[str] = None
    publish: bool
    override_ids: bool
    settings: Optional[str] = None
    input_source: Optional[str] = None
    delete_local_file: bool
    lookup_visible: bool
    headers: Optional[str] = None
    caching_enabled: bool
    force_to_ids: bool
    orgc_id: Optional[str] = None
    cache_timestamp: Optional[str] = None

    class Config:
        orm_mode = True
