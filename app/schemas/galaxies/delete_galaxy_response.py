from pydantic import BaseModel


class GalaxyDeleteResponse(BaseModel):
    class Config:
        orm_mode: True
