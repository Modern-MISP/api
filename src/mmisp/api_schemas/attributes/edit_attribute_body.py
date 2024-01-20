from pydantic import BaseModel


class EditAttributeBody(BaseModel):
    # -- optional
    category: str
    value: str
    to_ids: bool
    distribution: str
    comment: str
    disable_correlation: bool

    class Config:
        orm_mode = True
