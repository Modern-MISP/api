from pydantic import BaseModel


class AttributeDeleteResponse(BaseModel):
    message: str

    class Config:
        orm_mode = True
