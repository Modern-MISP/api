from pydantic import BaseModel


class ToggleEnableWarninglistsResponse(BaseModel):
    saved: bool
    success: str | None = None
    errors: str | None = None

    class Config:
        orm_mode = True
