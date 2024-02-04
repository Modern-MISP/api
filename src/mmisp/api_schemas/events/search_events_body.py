from pydantic import BaseModel


class SearchEventsBody(BaseModel):
    returnFormat: str
    page: int | None = None
    limit: int | None = None
    value: str | None = None
    type: str | None = None
    category: str | None = None
    org: str | None = None
    tags: list[str] | None = None
    event_tags: list[str] | None = None
    searchall: str | None = None
    from_: str | None = None
    to: str | None = None
    last: int | None = None
    eventid: str | None = None
    withAttachments: bool | None = None
    sharinggroup: list[str] | None = None
    metadata: bool | None = None
    uuid: str | None = None
    publish_timestamp: str | None = None
    timestamp: str | None = None
    published: bool | None = None
    enforceWarninglist: bool | None = None
    sgReferenceOnly: bool | None = None
    requested_attributes: list[str] | None = None
    includeContext: bool | None = None
    headerless: bool | None = None
    includeWarninglistHits: bool | None = None
    attackGalaxy: str | None = None
    to_ids: bool | None = None
    deleted: bool | None = None
    excludeLocalTags: bool | None = None
    date: str | None = None
    includeSightingdb: bool | None = None
    tag: str | None = None
    object_relation: str | None = None
    threat_level_id: str | None = None

    class Config:
        orm_mode = True
