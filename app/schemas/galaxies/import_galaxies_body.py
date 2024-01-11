from pydantic import BaseModel


class GalaxyImportBody(BaseModel):
    class Config:
        orm_mode = True
