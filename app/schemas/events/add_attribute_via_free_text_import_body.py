from pydantic import BaseModel


class EventsFreeTextImportAttributesBody(BaseModel):
    value: str

    class Config:
        orm_mode = True


class EventsFreeTextImportBody(BaseModel):
    Attribute: EventsFreeTextImportAttributesBody

    class Config:
        orm_mode = True
