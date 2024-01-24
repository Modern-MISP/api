from pydantic import BaseModel


class AuthKeyDeleteSchema(BaseModel):
    saved: bool = False
    success: bool = False
    name: str = ""
    message: str = ""
    url: str = ""
