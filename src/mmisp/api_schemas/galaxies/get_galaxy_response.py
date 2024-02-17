from pydantic import BaseModel

from .export_galaxies_response import ExportGalaxyClusterResponse
from .get_all_search_galaxies_response import GetAllSearchGalaxiesAttributes


class GetGalaxyResponse(BaseModel):
    Galaxy: GetAllSearchGalaxiesAttributes
    GalaxyCluster: list[ExportGalaxyClusterResponse]

    class Config:
        orm_mode = True
