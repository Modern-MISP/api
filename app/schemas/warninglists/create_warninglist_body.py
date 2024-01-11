from pydantic import BaseModel, Field

from .warninglists import Type, Category


class CreateWarninglistBody(BaseModel):
    name: str = Field(max_length=255)
    type: Type
    description: str = Field(max_length=65535)
    category: Category
    accepted_attribute_type: str
    values: str = Field(max_length=65535)