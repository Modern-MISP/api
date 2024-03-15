from pydantic import BaseModel


class GetSelectedWarninglistsBody(BaseModel):
    value: str | None = None
    enabled: bool | None = None

    class Config:
        orm_mode = True
