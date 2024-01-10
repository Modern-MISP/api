from pydantic import BaseModel


class SightingOrganisationResponse(BaseModel):
    id: str
    uuid: str
    name: str


class SightingAttributesResponse(BaseModel):
    id: str
    attribute_id: str
    event_id: str
    org_id: str
    date_sighting: str
    uuid: str
    source: str
    type: str
    attribute_uuid: str
    organisation: SightingOrganisationResponse


class SightingGetResponse(BaseModel):
    root: list[SightingAttributesResponse]

    class Config:
        orm_mode = True
