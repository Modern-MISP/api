from datetime import datetime

from pydantic import BaseModel


class Organisation(BaseModel):
    id: str
    name: str
    date_created: datetime
    date_modified: datetime
    description: str | None = None
    type: str
    nationality: str | None = None
    sector: str | None = None
    created_by: str
    uuid: str
    contacts: str | None = None
    local: bool
    """organisation gains access to the local instance, otherwise treated as external"""
    restricted_to_domain: str | None = None
    landingpage: str | None = None

    class Config:
        orm_mode = True
