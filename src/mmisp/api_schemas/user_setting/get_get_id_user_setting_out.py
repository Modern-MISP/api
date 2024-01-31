from pydantic import BaseModel


class Position(BaseModel):
    x: str
    y: str
    width: str
    height: str


class Value(BaseModel):
    widget: str
    position: Position


class UserSettingGet(BaseModel):
    id: str
    setting: str
    value: Value
    user_id: str
    timestamp: str
