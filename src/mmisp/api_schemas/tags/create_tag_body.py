from pydantic import BaseModel, Field


class TagCreateBody(BaseModel):
    name: str = Field(min_length=1)
    colour: str = Field(min_length=7)
    exportable: bool
    org_id: str | None = None
    user_id: str | None = None
    hide_tag: bool | None = None
    numerical_value: str | None = None
    is_galaxy: bool | None = None
    is_custom_galaxy: bool | None = None
    inherited: bool | None = None

    class Config:
        orm_mode = True
