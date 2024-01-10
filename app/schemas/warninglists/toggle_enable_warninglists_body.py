from pydantic import BaseModel

class ToggleEnableWarninglistsBody(BaseModel):
    id: str | list[str]
    name: str | list[str]
    enabled: bool