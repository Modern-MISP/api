from pydantic import BaseModel

class DeleteWarninglistResponse(BaseModel):
    saved: bool
    success: bool
    id: str
    name: str
    message: str
    url: str