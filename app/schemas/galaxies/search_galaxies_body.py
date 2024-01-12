from pydantic import BaseModel


class SearchGalaxiesBody(BaseModel):
    class Config:
        orm_mode = True
