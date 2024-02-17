from pydantic import BaseModel

from .get_galaxy_response import GetGalaxyClusterResponse


class ImportGalaxyGalaxy(BaseModel):
    uuid: str


class ImportGalaxyBody(BaseModel):
    GalaxyCluster: GetGalaxyClusterResponse
    Galaxy: ImportGalaxyGalaxy

    class Config:
        orm_mode = True
