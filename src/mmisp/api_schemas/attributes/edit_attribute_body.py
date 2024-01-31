from pydantic import BaseModel


class EditAttributeBody(BaseModel):
    category: str | None = None
    value: str | None = None
    to_ids: bool | None = None
    distribution: str | None = None
    comment: str | None = None
    disable_correlation: bool | None = None

    class Config:
        orm_mode = True
