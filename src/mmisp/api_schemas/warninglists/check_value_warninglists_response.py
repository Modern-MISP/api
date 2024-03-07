from pydantic import BaseModel


class NameWarninglist(BaseModel):
    id: int
    name: str


class ValueWarninglistsResponse(BaseModel):
    value: str
    Warninglist: list[NameWarninglist] | None


class CheckValueWarninglistsResponse(BaseModel):
    response: list[ValueWarninglistsResponse]

    class Config:
        orm_mode = True
