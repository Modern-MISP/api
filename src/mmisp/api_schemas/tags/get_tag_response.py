from pydantic import BaseModel


class TagAttributesResponse(BaseModel):
    id: str
    name: str
    colour: str
    exportable: bool
    org_id: str
    user_id: str
    hide_tag: bool
    numerical_value: str | None = None
    is_galaxy: bool
    is_custom_galaxy: bool
    inherited: bool | None = None


class TagGetResponse(BaseModel):
    tags: list[TagAttributesResponse]

    class Config:
        orm_mode = True
