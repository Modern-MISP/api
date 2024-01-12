from pydantic import BaseModel


class AttachClusterGalaxyBody(BaseModel):
    class Config:
        orm_mode = True
