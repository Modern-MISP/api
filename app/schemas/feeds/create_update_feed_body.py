from pydantic import BaseModel


class FeedCreateAndUpdateBody(BaseModel):
    name: str
    provider: str
    url: str
    rules: str
    enabled: str
    distribution: str
    sharing_group_id: str
    tag_id: str
    source_format: str
    fixed_event: str
    delta_merge: str
    event_id: str
    publish: str
    override_ids: str
    input_source: str
    delete_local_file: str
    lookup_visible: str
    headers: str
    caching_enabled: str
    force_to_ids: str
    orgc_id: str

    class Config:
        orm_mode = True
