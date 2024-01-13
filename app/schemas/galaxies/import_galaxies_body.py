from pydantic import BaseModel

from .export_galaxies_response import ExportGalaxyResponse


class ImportGalaxyGalaxy(BaseModel):
    uuid: str


class ImportGalaxyBody(BaseModel):
    GalaxyCluster: ExportGalaxyResponse
    Galaxy: ImportGalaxyGalaxy

    class Config:
        orm_mode = True
