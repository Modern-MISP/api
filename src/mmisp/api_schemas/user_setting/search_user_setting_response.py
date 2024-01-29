from pydantic import BaseModel

from .get_get_id_user_setting_response import Value


class UserSettingSearch(BaseModel):
    id: str
    setting: str
    value: Value
    user_id: str
    timestamp: str
