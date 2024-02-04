from pydantic import BaseModel


class IndexEventsBody(BaseModel):
    page: int | None = None
    limit: int | None = None
    sort: int | None = None
    direction: int | None = None
    minimal: bool | None = None
    attribute: str | None = None
    eventid: str | None = None
    datefrom: str | None = None
    dateuntil: str | None = None
    org: str | None = None
    eventinfo: str | None = None
    tag: str | None = None
    tags: list[str] | None = None
    distribution: str | None = None
    sharinggroup: str | None = None
    analysis: str | None = None
    threatlevel: str | None = None
    email: str | None = None
    hasproposal: str | None = None
    timestamp: str | None = None
    publish_timestamp: str | None = None
    searchDatefrom: str | None = None
    searchDateuntil: str | None = None

    class Config:
        orm_mode = True
