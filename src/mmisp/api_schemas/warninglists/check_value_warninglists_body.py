from pydantic import BaseModel


class CheckValueWarninglistsBody(BaseModel):
    value: str

    class Config:
        orm_mode = True
