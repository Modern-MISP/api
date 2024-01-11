from pydantic import BaseModel


class GalaxyAttachClusterResponse(BaseModel):
    class Config:
        orm_mode: True
