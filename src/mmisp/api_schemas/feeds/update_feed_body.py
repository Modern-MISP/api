from pydantic import BaseModel


class FeedUpdateBody(BaseModel):
    name: str | None = None
    provider: str | None = None
    url: str | None = None
    rules: str | None = None
    enabled: bool | None = None
    distribution: str | None = None
    sharing_group_id: str | None = None
    tag_id: str | None = None
    default: bool | None = None
    source_format: str | None = None
    fixed_event: bool | None = None
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

    class Config:
        orm_mode = True
