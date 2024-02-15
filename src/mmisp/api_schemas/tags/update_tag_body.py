from pydantic import BaseModel


class TagUpdateBody(BaseModel):
    name: str | None = None
    colour: str | None = None
    exportable: bool | None = None
    org_id: str | None = None
    user_id: str | None = None
    hide_tag: bool | None = None
    numerical_value: str | None = None
    # is_galaxy: bool | None = None
    # is_custom_galaxy: bool | None = None
    inherited: bool | None = None

    class Config:
        orm_mode = True
