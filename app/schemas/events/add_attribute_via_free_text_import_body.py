from pydantic import BaseModel


class EventsFreeTextImportAttributesBody(BaseModel):
    value: str


class EventsFreeTextImportBody(BaseModel):
    Attribute: EventsFreeTextImportAttributesBody

    class Config:
        orm_mode = True
