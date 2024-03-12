from pydantic import BaseModel


class UserSettingSchema(BaseModel):
    id: str
    setting: str
    value: dict | list
    user_id: str
    timestamp: str


class UserSettingResponse(BaseModel):
    UserSetting: UserSettingSchema
