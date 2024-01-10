from pydantic import BaseModel


class StartLoginBody(BaseModel):
    email: str
