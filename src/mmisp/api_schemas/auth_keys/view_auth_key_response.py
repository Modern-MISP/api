from datetime import datetime

from pydantic import BaseModel

from .search_get_all_auth_keys_users_response import SearchGetAuthKeysResponseItemUser


class ViewAuthKeyResponseWrapper(BaseModel):
    id: str
    uuid: str
    authkey_start: str
    authkey_end: str
    created: datetime
    expiration: int
    read_only: bool
    user_id: str
    comment: str
    allowed_ips: list[str] | None = None
    unique_ips: list[str] | None = []


class ViewAuthKeysResponse(BaseModel):
    AuthKey: ViewAuthKeyResponseWrapper
    User: SearchGetAuthKeysResponseItemUser
