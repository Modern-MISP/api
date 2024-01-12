from pydantic import BaseModel


class AttachClusterGalaxyResponse(BaseModel):
    class Config:
        orm_mode = True
