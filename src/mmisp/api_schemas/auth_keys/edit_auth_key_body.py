from pydantic import BaseModel


class EditAuthKeyBody(BaseModel):
    read_only: bool | None = None
    comment: str | None = None
    allowed_ips: list[str] | None = None
    expiration: int | None = None
