from pydantic import BaseModel


class AuthKey(BaseModel):
    id: str
    uuid: str
    authkey_start: str
    authkey_end: str
    created: str
    expiration: str
    read_only: bool
    user_id: str
    comment: str
    allowed_ips: list[str]
    last_used: str
