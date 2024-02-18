from pydantic import BaseModel


class AddAuthKeyBody(BaseModel):
    uuid: str | None = None
    read_only: bool | None = None
    user_id: str | None = None
    comment: str | None = None
    allowed_ips: list[str] | None = None
    expiration: int | str | None = 0
