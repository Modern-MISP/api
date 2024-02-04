from pydantic import BaseModel

from mmisp.api_schemas.attributes.get_all_attributes_response import GetAllAttributesResponse


class ObjectWithAttributesSearchResponse(BaseModel):
    id: str
    description: str
    name: str
    meta_category: str
    distribution: str
    event_id: str | None = None
    template_uuid: str | None = None
    template_version: str | None = None
    uuid: str | None = None
    timestamp: str | None = None
    sharing_group_id: str | None = None
    comment: str | None = None
    deleted: bool | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    attributes: list[GetAllAttributesResponse] | None = None


class ObjectResponse(BaseModel):
    object: ObjectWithAttributesSearchResponse

    class Config:
        orm_mode = True


class ObjectSearchResponse(BaseModel):
    response: list[ObjectResponse]

    class Config:
        orm_mode = True
