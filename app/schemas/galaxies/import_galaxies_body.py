from pydantic import BaseModel


class ImportGalaxyBody(BaseModel):
    class Config:
        orm_mode = True
