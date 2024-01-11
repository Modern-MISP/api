from pydantic import BaseModel


class AddAttributeBody(BaseModel):
    # -- mandatory
    value: str
    type: str
    # -- optional
    category: str
    to_ids: bool
    distribution: str
    comment: str
    disable_correlation: bool

    class Config:
        orm_mode = True
