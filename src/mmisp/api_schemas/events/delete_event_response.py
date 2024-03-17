from pydantic import BaseModel


class DeleteEventResponse(BaseModel):
    saved: bool
    success: bool | None = None
    name: str
    message: str
    url: str
    id: str
    errors: str | None = None

    class Config:
        orm_mode = True
