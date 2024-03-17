from pydantic import BaseModel


class NameWarninglist(BaseModel):
    id: str
    name: str
    matched: str


class CheckValueResponse(BaseModel):
    value: list[NameWarninglist]

    class Config:
        orm_mode = True
