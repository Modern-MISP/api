from pydantic import BaseModel


class AuthKeyEdit(BaseModel):
    read_only: bool
    comment: str
    allowed_ips: list[str]
