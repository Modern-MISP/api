from pydantic import BaseModel


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

    class Organisation:
        id: str
        uuid: str
        name: str

    class Config:
        orm_mode = True
