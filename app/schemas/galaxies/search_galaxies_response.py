from pydantic import BaseModel


class GalaxySearchResponse(BaseModel):
    class Config:
        orm_mode: True
