from pydantic import BaseModel


class EditAuthKeyResponseUser(BaseModel):
    id: str
    org_id: str


class EditAuthKeyResponseAuthKey(BaseModel):
    id: str
    uuid: str
    authkey_start: str
    authkey_end: str
    created: str
    expiration: str
    read_only: bool
    user_id: str
    comment: str
    allowed_ips: str | None = None


class EditAuthKeyResponse(BaseModel):
    AuthKey: EditAuthKeyResponseAuthKey
    User: EditAuthKeyResponseUser
