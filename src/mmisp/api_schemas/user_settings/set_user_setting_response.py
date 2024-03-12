from pydantic import BaseModel


class SetUserSettingResponseUserSetting(BaseModel):
    id: str
    setting: str
    value: dict | list
    user_id: str
    timestamp: str


class SetUserSettingResponse(BaseModel):
    UserSetting: SetUserSettingResponseUserSetting
