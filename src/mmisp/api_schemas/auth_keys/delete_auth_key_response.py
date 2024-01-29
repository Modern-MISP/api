from pydantic import BaseModel


class DeleteAuthKeyResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str
