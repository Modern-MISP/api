from pydantic import BaseModel


class SetUserSettingBody(BaseModel):
    value: dict | list
