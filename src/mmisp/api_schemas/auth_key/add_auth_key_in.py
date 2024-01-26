from pydantic import BaseModel


class AuthKeyAdd(BaseModel):
    uuid: str
    read_only: bool
    user_id: str
    comment: str
    allowed_ips: list[str]
