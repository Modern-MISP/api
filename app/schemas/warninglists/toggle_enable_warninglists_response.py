from pydantic import BaseModel

class ToggleEnableWarninglistsResponse(BaseModel):
    saved: bool
    success: str