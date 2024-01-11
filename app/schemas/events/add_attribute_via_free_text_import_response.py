from pydantic import BaseModel


class EventsFreeTextImportResponse(BaseModel):
    comment: str
    value: str
    original_value: str
    to_ids: str
    type: str
    category: str
    distribution: str

    class Config:
        orm_mode = True
