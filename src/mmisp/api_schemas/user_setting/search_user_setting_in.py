from pydantic import BaseModel


class UserSettingSearchIn(BaseModel):
    id: str = ""
    setting: str = ""
    user_id: str = ""
