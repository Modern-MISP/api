from pydantic import BaseModel


class SearchUserSettingBody(BaseModel):
    id: str
    setting: str
    user_id: str
