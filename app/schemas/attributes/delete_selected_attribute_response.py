from pydantic import BaseModel


class AttributeDeleteSelectedResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str
    id: str

    class Config:
        orm_mode = True
