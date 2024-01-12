from pydantic import BaseModel


class ForceUpdateGalaxyResponse(BaseModel):
    class Config:
        orm_mode = True
