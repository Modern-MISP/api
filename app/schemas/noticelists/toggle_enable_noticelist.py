from pydantic import Field, BaseModel

class ToggleEnableNoticelist(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str
    id: int