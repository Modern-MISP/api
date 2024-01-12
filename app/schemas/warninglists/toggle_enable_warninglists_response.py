from pydantic import BaseModel


class ToggleEnableWarninglistsResponse(BaseModel):
    saved: bool
    success: str

    class Config:
        orm_mode = True
