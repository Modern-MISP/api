from pydantic import BaseModel


class AttachClusterGalaxyResponse(BaseModel):
    saved: bool
    succes: str
    check_publish: bool

    class Config:
        orm_mode = True
