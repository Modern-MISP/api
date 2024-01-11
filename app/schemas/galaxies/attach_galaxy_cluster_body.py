from pydantic import BaseModel


class GalaxyAttachClusterBody(BaseModel):
    class Config:
        orm_mode: True
