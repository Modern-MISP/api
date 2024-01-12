from pydantic import BaseModel


class ExportGalaxyBody(BaseModel):
    class Config:
        orm_mode = True
