from pydantic import BaseModel


class DeleteUserSettingResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str
