from pydantic import BaseModel


class AuthKeyDelete(BaseModel):
    saved: bool = False
    success: bool = False
    name: str = ""
    message: str = ""
    url: str = ""