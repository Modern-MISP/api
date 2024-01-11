from pydantic import BaseModel


class GalaxiesGetResponse(BaseModel):
    class Config:
        orm_mode = True
