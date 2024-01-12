from pydantic import BaseModel


class ExportGalaxyResponse(BaseModel):
    class Config:
        orm_mode = True
