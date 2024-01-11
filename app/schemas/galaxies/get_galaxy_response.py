from pydantic import BaseModel


class GalaxyGetResponse(BaseModel):
    class Config:
        orm_mode: True
