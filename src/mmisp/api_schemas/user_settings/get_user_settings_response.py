from pydantic import BaseModel


class UserSetting(BaseModel):
    id: str
    setting: str
    value: dict
    user_id: str
    timestamp: str


class UserSettingResponse(BaseModel):
    UserSetting: UserSetting
