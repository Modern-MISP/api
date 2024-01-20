from pydantic import BaseModel


class ToggleEnableNoticelist(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str
    id: int

    class Config:
        orm_mode = True
