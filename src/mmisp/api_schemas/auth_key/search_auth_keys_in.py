from pydantic import BaseModel


class AuthKeySearch(BaseModel):
    page: int = 1
    limit: int = 0
    id: str = ""
    uuid: str = ""
    authkey_start: str = ""
    authkey_end: str = ""
    created: str = ""
    expiration: str = ""
    read_only: bool = True
    user_id: str = ""
    comment: str = ""
    allowed_ips: list[str]
    last_used: str = ""
