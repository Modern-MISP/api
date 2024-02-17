from pydantic import BaseModel


class ExportGalaxyAttributes(BaseModel):
    default: bool
    custom: bool | None = None
    distribution: str
    format: str | None = None
    download: bool | None = None


class ExportGalaxyBody(BaseModel):
    Galaxy: ExportGalaxyAttributes

    class Config:
        orm_mode = True
