from pydantic import BaseModel


class GalaxyUpdateResponse(BaseModel):
    class Config:
        orm_mode: True
