from pydantic import BaseModel


class GetGalaxyResponse(BaseModel):
    class Config:
        orm_mode = True
