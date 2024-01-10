from pydantic import BaseModel


class AuthKeyAdd(BaseModel):
    uuid: str = ""
    read_only: bool = True
    user_id: str = ""
    comment: str = ""
    allowed_ips: list[str]
