from pydantic import BaseModel


class ObjectDeleteResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True
