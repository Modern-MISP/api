from pydantic import BaseModel


class CheckValueWarninglistsBody(BaseModel):
    value: list[str]

    class Config:
        orm_mode = True
