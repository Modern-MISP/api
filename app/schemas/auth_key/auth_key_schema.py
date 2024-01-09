from pydantic import BaseModel


class AuthKey(BaseModel):
    id: str = ""
    uuid: str = ""
    authkey_start: str = ""
    authkey_end: str = ""
    created: str = ""
    expiration: str = ""
    read_only: bool = False
    user_id: str = ""
    comment: str = ""
    allowed_ips: str = ""  # Stringified JSON Array of IP addresses
    last_used: str = ""
    unique_ips: list[str] = [""]
    authkey_raw: str = ""
