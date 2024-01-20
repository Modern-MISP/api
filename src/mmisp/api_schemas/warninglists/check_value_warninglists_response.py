from pydantic import BaseModel


class NameWarninglist(BaseModel):
    id: int
    name: str


class CheckValueWarninglistsResponse(BaseModel):
    response: str
    NameWarninglist: list[NameWarninglist]

    class Config:
        orm_mode = True
