from pydantic import BaseModel

from ...api_schemas.attributes.add_attribute_body import AddAttributeBody


class AddEventBody(BaseModel):
    info: str  # mandatory
    # -- optional
    threat_level_id: str
    analysis: str
    distribution: str
    sharing_group_id: str
    published: bool
    timestamp: str
    date: str
    Attribute: list[AddAttributeBody]
    Object: list[str]
    Shadow_Attribute: list[str]
    EventTag: list[str]

    class Config:
        orm_mode = True
