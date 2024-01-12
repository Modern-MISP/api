from pydantic import BaseModel


class DeleteEventsResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str
    errors: str

    class Config:
        orm_mode = True
