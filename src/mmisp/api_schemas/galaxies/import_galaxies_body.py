from pydantic import BaseModel

from .export_galaxies_response import ExportGalaxyClusterResponse


class ImportGalaxyGalaxy(BaseModel):
    uuid: str


class ImportGalaxyBody(BaseModel):
    GalaxyCluster: ExportGalaxyClusterResponse
    Galaxy: ImportGalaxyGalaxy

    class Config:
        orm_mode = True
