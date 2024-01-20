from pydantic import BaseModel


class AttachClusterGalaxyAttributes(BaseModel):
    target_id: int


class AttachClusterGalaxyBody(BaseModel):
    Galaxy: AttachClusterGalaxyAttributes

    class Config:
        orm_mode = True
