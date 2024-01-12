from pydantic import BaseModel


class GetAllGalaxiesResponse(BaseModel):
    class Config:
        orm_mode = True
