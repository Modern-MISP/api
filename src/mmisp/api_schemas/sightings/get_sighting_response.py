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
    event_id: str | None = None
    org_id: str | None = None
    date_sighting: str | None = None
    source: str | None = None
    type: str | None = None
    Organisation: SightingOrganisationResponse | None = None


class SightingsGetResponse(BaseModel):
    sightings: list[SightingAttributesResponse]

    class Config:
        orm_mode = True
