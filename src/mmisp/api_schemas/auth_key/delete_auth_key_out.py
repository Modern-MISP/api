from pydantic import BaseModel


class AuthKeyDeleteSchema(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str
