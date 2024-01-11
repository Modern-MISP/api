from pydantic import BaseModel


class AttributeEditBody(BaseModel):
    # -- optional
    category: str
    value: str
    to_ids: bool
    distribution: str
    comment: str
    disable_correlation: bool

    class Config:
        orm_mode = True
