from pydantic import BaseModel


class EventsIndexBody(BaseModel):
    # -- optional
    all: str
    attribute: str
    published: bool
    eventid: str
    datefrom: str
    dateuntil: str
    org: str
    eventinfo: str
    tag: str
    tags: list[str]
    distribution: str
    sharinggroup: str
    analysis: str
    threatlevel: str
    email: str
    hasproposal: bool
    timestamp: str
    publishtimestamp: str
    publish_timestamp: str
    minimal: bool

    class Config:
        orm_mode = True
