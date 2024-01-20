from pydantic import BaseModel


class SearchGalaxiesBody(BaseModel):
    value: str

    class Config:
        orm_mode = True
