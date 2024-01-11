from pydantic import BaseModel


class GalaxyExportBody(BaseModel):
    class Config:
        orm_mode = True
