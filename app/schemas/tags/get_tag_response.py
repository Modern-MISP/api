from pydantic import BaseModel


class TagAttributesResponse(BaseModel):
    id: str
    name: str
    colour: str
    exportable: bool
    org_id: str
    user_id: str
    hide_tag: bool
    numerical_value: str
    is_galaxy: bool
    is_custom_galaxy: bool
    inherited: int  # omitted
    attribute_count: int  # new
    count: int  # new
    favourite: bool  # new
    local_only: bool  # new


class TagGetResponse(BaseModel):
    tag: list[TagAttributesResponse]

    class Config:
        orm_mode = True
