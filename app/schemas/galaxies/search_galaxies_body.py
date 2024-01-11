from pydantic import BaseModel


class GalaxySearchBody(BaseModel):
    class Config:
        orm_mode: True
