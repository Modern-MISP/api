from pydantic import BaseModel


class EditAuthKeyBody(BaseModel):
    read_only: bool
    comment: str
    allowed_ips: list[str]
