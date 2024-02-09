from pydantic import BaseModel

from mmisp.api_schemas.attributes.add_attribute_body import AddAttributeBody

# class ObjectCreateRequirementBody(BaseModel):
#     requirement: list[str] | None = None
#     requirement_type: list[str] | None = None


class ObjectCreateBody(BaseModel):
    name: str
    meta_category: str | None = None
    description: str | None = None
    action: str | None = None
    template_id: str | None = None
    template_uuid: str | None = None
    template_name: str | None = None
    template_version: str | None = None
    template_description: str | None = None
    update_template_available: bool | None = None
    event_id: str | None = None
    distribution: str | None = None
    sharing_group_id: str
    comment: str
    deleted: bool | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    attributes: list[AddAttributeBody]

    class Config:
        orm_mode = True
