from pydantic import BaseModel

class UpdateAllWarninglistsResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str