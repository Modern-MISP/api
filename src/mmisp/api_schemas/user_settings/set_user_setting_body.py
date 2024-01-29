from pydantic import BaseModel

from .get_get_id_user_setting_response import Position


class SetUserSettingBody(BaseModel):
    widget: str
    position: Position
