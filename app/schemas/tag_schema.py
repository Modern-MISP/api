from pydantic import BaseModel


class TagSchema(BaseModel):
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
    inherited: int

    class Config:
        orm_mode = True
