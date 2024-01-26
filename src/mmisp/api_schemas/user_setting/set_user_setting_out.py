from pydantic import BaseModel

from .get_get_id_user_setting_out import Value


class UserSettingSet(BaseModel):
    id: str
    setting: str
    value: Value
    user_id: str
    timestamp: str
