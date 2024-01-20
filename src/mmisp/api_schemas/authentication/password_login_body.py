from pydantic import BaseModel


class PasswordLoginBody(BaseModel):
    email: str
    password: str
