from pydantic import BaseModel


class UserSettings(BaseModel):
    id: str = ""
    setting: str = ""
    value: dict = {
        "widget": str,
        "position": {"x": int, "y": int, "width": int, "height": int},
    }
    user_id: str = ""
    timestamp: str = ""
