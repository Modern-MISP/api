from pydantic import BaseModel


class EventsDeleteResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str
    errors: str

    class Config:
        orm_mode = True
