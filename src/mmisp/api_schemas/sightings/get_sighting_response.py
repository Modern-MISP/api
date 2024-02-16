from pydantic import BaseModel


class SightingOrganisationResponse(BaseModel):
    id: str
    uuid: str
    name: str


class SightingAttributesResponse(BaseModel):  # todo: validate 'None = None'
    id: str
    uuid: str | None = None
    attribute_id: str | None = None
    event_id: str | None = None
    org_id: str | None = None
    date_sighting: str | None = None
    source: str | None = None
    type: str | None = None
    organisation: SightingOrganisationResponse | None = None


class SightingGetResponse(BaseModel):
    root: list[SightingAttributesResponse]

    class Config:
        orm_mode = True
