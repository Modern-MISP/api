from fastapi import FastAPI
from pydantic import BaseModel


class Events(BaseModel):
    id: str = ""
    org_id: str = ""
    distribution: str = ""
    orgc_id: str = ""
    uuid: str = ""
    date: str = ""
    published: bool = False
    analysis: str = ""
    attribute_count: str = ""
    timestamp: str = ""
    sharing_group_id: str = ""
    proposal_email_lock: bool
    locked: bool
    threat_level_id: str = ""
    publish_timestamp: str = ""
    sighting_timestamp: str = ""
    disable_correlation: bool = False
    extends_uuid: str = ""
    event_creator_email: str = ""


app = FastAPI()
