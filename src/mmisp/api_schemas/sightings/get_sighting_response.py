from pydantic import BaseModel


class SightingOrganisationResponse(BaseModel):
    id: str
    uuid: str
    name: str


class SightingAttributesResponse(BaseModel):
    id: str
    uuid: str
    attribute_id: str
    attribute_uuid: str
    event_id: str
    org_id: str
    date_sighting: str
    source: str | None = None
    type: str | None = None
    organisation: SightingOrganisationResponse


class SightingsGetResponse(BaseModel):
    sightings: list[SightingAttributesResponse]

    class Config:
        orm_mode = True
