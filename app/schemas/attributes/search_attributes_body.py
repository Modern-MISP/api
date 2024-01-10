from pydantic import BaseModel


class AttributeRestSearchBody(BaseModel):
    return_Format: str  # mandatory
    # -- optional
    page: int
    limit: int
    value: str
    type: str
    category: str
    org: str
    tags: list[str]
    date: str
    last: str
    eventid: str
    withAttachments: bool
    uuid: str
    publish_timestamp: str
    timestamp: str
    attribute_timestamp: str
    enforceWarninglist: bool
    to_ids: bool
    deleted: bool
    includeEventUuid: bool
    includeEventTags: bool
    event_timestamp: str
    threat_level_id: str
    eventinfo: str
    sharinggroup: str
    includeProposals: bool
    includeDecayScore: bool
    includeFullModel: bool
    decayingModel: str
    excludeDecayed: bool
    score: str
    first_seen: str
    last_seen: str

    class Config:
        orm_mode = True
