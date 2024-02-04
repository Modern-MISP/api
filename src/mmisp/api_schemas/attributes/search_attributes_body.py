from pydantic import BaseModel


class SearchAttributesBody(BaseModel):
    returnFormat: str
    page: int | None = None
    limit: int | None = None
    value: str | None = None
    type: str | None = None
    category: str | None = None
    org: str | None = None
    tags: list[str] | None = None
    date: str | None = None
    last: str | None = None
    event_id: str | None = None
    withAttachments: bool | None = None
    uuid: str | None = None
    publish_timestamp: str | None = None
    timestamp: str | None = None
    attribute_timestamp: str | None = None
    enforceWarninglist: bool | None = None
    to_ids: bool | None = None
    deleted: bool | None = None
    includeEventUuid: bool | None = None
    includeEventTags: bool | None = None
    event_timestamp: str | None = None
    threat_level_id: str | None = None
    eventinfo: str | None = None
    sharinggroup: str | None = None
    includeProposals: bool | None = None
    includeDecayScore: bool | None = None
    includeFullModel: bool | None = None
    decayingModel: str | None = None
    excludeDecayed: bool | None = None
    score: str | None = None
    first_seen: str | None = None
    last_seen: str | None = None

    class Config:
        orm_mode = True
