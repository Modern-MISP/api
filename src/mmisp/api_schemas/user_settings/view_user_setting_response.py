from pydantic import BaseModel


class ViewUserSettingResponseUserSetting(BaseModel):
    id: str
    setting: str
    value: dict
    user_id: str
    timestamp: str


class ViewUserSettingResponse(BaseModel):
    UserSetting: ViewUserSettingResponseUserSetting
