from pydantic import BaseModel

from .get_all_search_galaxies_response import GetAllSearchGalaxiesAttributes
from .export_galaxies_response import ExportGalaxyResponse


class GetGalaxyResponse(BaseModel):
    Galaxy: GetAllSearchGalaxiesAttributes
    GalaxyCluster: list[ExportGalaxyResponse]

    class Config:
        orm_mode = True
