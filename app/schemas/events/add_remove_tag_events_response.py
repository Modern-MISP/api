from pydantic import BaseModel


class EventsTagResponse(BaseModel):
    saved: bool
    success: str
    check_publish: bool
    errors: str

    class Config:
        orm_mode = True
