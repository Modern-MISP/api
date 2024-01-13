from pydantic import BaseModel


class ExportGalaxyAttributes(BaseModel):
    default: bool
    custom: bool
    distribution: str
    format: str
    download: bool


class ExportGalaxyBody(BaseModel):
    Galaxy: ExportGalaxyAttributes

    class Config:
        orm_mode = True
