from pydantic import BaseModel


class AddAttributeViaFreeTextImportEventAttributes(BaseModel):
    value: str


class AddAttributeViaFreeTextImportEventBody(BaseModel):
    Attribute: AddAttributeViaFreeTextImportEventAttributes

    class Config:
        orm_mode = True
