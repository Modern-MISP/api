from pydantic import BaseModel

class UserSettingDelete(BaseModel):
    saved: bool = False
    success: bool = False
    name: str = ""
    message: str = ""
    url: str = ""
