from pydantic import BaseModel, Field

from mmisp.api_schemas.attributes.add_attribute_body import AddAttributeBody


class ObjectCreateBody(BaseModel):
    name: str = Field(min_length=1)
    meta_category: str | None = None
    description: str | None = None
    distribution: str | None = None
    sharing_group_id: str = Field(min_length=1)
    comment: str = Field(min_length=1)
    deleted: bool | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    attributes: list[AddAttributeBody]

    class Config:
        orm_mode = True
