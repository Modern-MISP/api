from pydantic import BaseModel


class AddAttributeViaFreeTextImportToEventAttributes(BaseModel):
    value: str


class AddAttributeViaFreeTextImportToEventBody(BaseModel):
    Attribute: AddAttributeViaFreeTextImportToEventAttributes

    class Config:
        orm_mode = True
