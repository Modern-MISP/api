from pydantic import BaseModel


class UnpublishEventResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True
