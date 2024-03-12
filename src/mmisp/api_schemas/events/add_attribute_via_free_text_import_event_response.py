from pydantic import BaseModel


class AddAttributeViaFreeTextImportEventResponse(BaseModel):
    comment: str | None = None
    value: str
    original_value: str
    to_ids: str
    type: str
    category: str
    distribution: str

    class Config:
        orm_mode = True
