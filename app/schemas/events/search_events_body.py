from pydantic import BaseModel


class EventsRestSearchBody(BaseModel):
    returnFormat: str  # mandatory
    # -- optional
    page: int
    limit: int
    value: str
    type: str
    category: str
    org: str
    tag: str
    tags: list[str]
    event_tags: list[str]
    searchall: str
    date: str
    last: int
    eventid: str
    withAttachments: bool
    metadata: bool
    uuid: str
    published: bool
    publish_timestamp: str
    timestamp: str
    enforceWarninglist: bool
    sgReferenceOnly: bool
    eventinfo: str
    sharinggroup: str
    excludeLocalTags: bool
    threat_level_id: str

    class Config:
        orm_mode = True
