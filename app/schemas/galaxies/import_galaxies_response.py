from pydantic import BaseModel


class GalaxyImportResponse(BaseModel):
    class Config:
        orm_mode = True
