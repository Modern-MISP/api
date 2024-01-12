from pydantic import BaseModel


class ImportGalaxyResponse(BaseModel):
    class Config:
        orm_mode = True
