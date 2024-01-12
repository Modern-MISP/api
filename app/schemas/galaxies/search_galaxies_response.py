from pydantic import BaseModel


class SearchGalaxiesResponse(BaseModel):
    class Config:
        orm_mode = True
