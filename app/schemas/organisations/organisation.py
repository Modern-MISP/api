from pydantic import BaseModel


class Organisation(BaseModel):
    id: str
    name: str
    date_created: str
    date_modified: str
    description: str | None = None
    type: str
    nationality: str | None = None
    sector: str | None = None
    created_by: str
    uuid: str
    contacts: str | None = None
    local: bool
    restricted_to_domain: str | None = None
    landingpage: str | None = None
