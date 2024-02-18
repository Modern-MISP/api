from pydantic import BaseModel


class SearchAuthKeyBody(BaseModel):
    page: int | None = 0
    limit: int | None = 25
    id: str | None = None
    uuid: str | None = None
    authkey_start: str | None = None
    authkey_end: str | None = None
    created: str | None = None
    expiration: str | None = None
    read_only: bool | None = None
    user_id: str | None = None
    comment: str | None = None
    allowed_ips: str | list[str] | None = None
    last_used: str | None = None  # deprecated
