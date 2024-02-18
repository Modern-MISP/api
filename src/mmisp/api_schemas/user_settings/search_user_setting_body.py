from pydantic import BaseModel


class SearchUserSettingBody(BaseModel):
    id: str | None = None
    setting: str | None = None
    user_id: str | None = None
