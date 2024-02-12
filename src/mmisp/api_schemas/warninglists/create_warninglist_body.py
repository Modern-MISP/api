from pydantic import BaseModel, Field


class CreateWarninglistBody(BaseModel):
    name: str = Field(max_length=255)
    type: str
    description: str = Field(max_length=65535)
    default: bool
    category: str
    valid_attributes: str
    values: str = Field(max_length=65535)

    class Config:
        orm_mode = True
