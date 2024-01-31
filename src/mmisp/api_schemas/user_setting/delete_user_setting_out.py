from pydantic import BaseModel


class UserSettingDelete(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str
