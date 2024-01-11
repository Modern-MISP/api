from pydantic import BaseModel


class GalaxyExportResponse(BaseModel):
    class Config:
        orm_mode: True
