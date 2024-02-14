from pydantic import BaseModel


class AddRemoveTagEventsResponse(BaseModel):
    saved: bool
    success: str | None = None
    check_publish: bool | None = None
    errors: str | None = None

    class Config:
        orm_mode = True
