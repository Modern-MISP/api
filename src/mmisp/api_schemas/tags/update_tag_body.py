from pydantic import BaseModel


class TagUpdateBody(BaseModel):
    name: str | None = None
    colour: str | None = None
    exportable: bool | None = None
    org_id: str | None = None
    user_id: str | None = None
    hide_tag: bool | None = None
    numerical_value: str | None = None
    local_only: bool | None = None

    class Config:
        orm_mode = True
