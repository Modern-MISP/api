from pydantic import BaseModel


class NameWarninglist(BaseModel):
    id: str
    name: str
    matched: str

    class Config:
        orm_mode = True
