from pydantic import BaseModel


class AddAuthKeyResponseAuthKey(BaseModel):
    id: str
    uuid: str
    authkey_start: str
    authkey_end: str
    created: str
    expiration: str | None = "0"
    read_only: bool
    user_id: str
    comment: str | None = None
    allowed_ips: list[str] | None = None
    unique_ips: list[str]
    authkey_raw: str


class AddAuthKeyResponse(BaseModel):
    AuthKey: AddAuthKeyResponseAuthKey
