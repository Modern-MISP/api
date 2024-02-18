from pydantic import BaseModel

from .get_uid_user_setting_response import Value


class SearchUserSettingResponse(BaseModel):
    id: str
    setting: str
    value: Value
    user_id: str
    timestamp: str
