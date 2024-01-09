from pydantic import BaseModel


class OrganisationSchema(BaseModel):
    id: str
    uuid: str
    name: str


class SightingSchema(BaseModel):
    id: str
    attribute_id: str
    event_id: str
    org_id: str
    date_sighting: str
    uuid: str
    source: str
    type: str
    attribute_uuid: str
    Organisation: OrganisationSchema

    class Config:
        orm_mode = True


class SightingDeleteSchema(BaseModel):
    saved: str
    success: str
    name: str
    message: str
    url: str
