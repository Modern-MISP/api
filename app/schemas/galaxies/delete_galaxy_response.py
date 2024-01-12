from pydantic import BaseModel


class DeleteGalaxyResponse(BaseModel):
    class Config:
        orm_mode = True
