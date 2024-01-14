from pydantic import BaseModel, Field

from .warninglist import Type, Category


class CreateWarninglistBody(BaseModel):
    name: str = Field(max_length=255)
    type: Type
    description: str = Field(max_length=65535)
    category: Category
    accepted_attribute_type: str
    values: str = Field(max_length=65535)

    class Config:
        orm_mode = True
