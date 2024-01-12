from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.galaxies.delete_galaxy_response import DeleteGalaxyResponse
from ..schemas.galaxies.get_all_galaxies import GetAllGalaxiesResponse
from ..schemas.galaxies.get_galaxy_response import GetGalaxyResponse
from ..schemas.galaxies.search_galaxies_body import SearchGalaxiesBody
from ..schemas.galaxies.search_galaxies_response import SearchGalaxiesResponse
from ..schemas.galaxies.force_update_galaxies_response import ForceUpdateGalaxyResponse
from ..schemas.galaxies.import_galaxies_body import ImportGalaxyBody
from ..schemas.galaxies.import_galaxies_response import ImportGalaxyResponse
from ..schemas.galaxies.export_galaxies_body import ExportGalaxyBody
from ..schemas.galaxies.export_galaxies_response import ExportGalaxyResponse
from ..schemas.galaxies.attach_galaxy_cluster_body import AttachClusterGalaxyBody
from ..schemas.galaxies.attach_galaxy_cluster_response import (
    AttachClusterGalaxyResponse,
)

router = APIRouter(prefix="/galaxies", tags=["galaxies"])


# -- Delete


@router.delete("/delete/{galaxy_id}", deprecated=True)  # deprecated
@router.delete("/{galaxy_id}")  # new
async def galaxies_delete(
    galagxy_id: str, db: Session = Depends(get_db)
) -> DeleteGalaxyResponse:
    return DeleteGalaxyResponse()


# -- Get


@router.get("/")
async def galaxies_get(db: Session = Depends(get_db)) -> GetAllGalaxiesResponse:
    return GetAllGalaxiesResponse()


@router.get("/view/{galaxy_id}", deprecated=True)  # deprecated
@router.get("/{galaxy_id}")  # new
async def galaxies_getById(db: Session = Depends(get_db)) -> GetGalaxyResponse:
    return GetGalaxyResponse()


# -- Post


@router.post("/")
async def galaxies_post(
    body: SearchGalaxiesBody, db: Session = Depends(get_db)
) -> SearchGalaxiesResponse:
    return SearchGalaxiesResponse()


@router.post("/update")
async def galaxies_update(db: Session = Depends(get_db)) -> ForceUpdateGalaxyResponse:
    return ForceUpdateGalaxyResponse


@router.post("/import")
async def galaxies_import(
    body: ImportGalaxyBody, db: Session = Depends(get_db)
) -> ImportGalaxyResponse:
    return ImportGalaxyResponse()


@router.post("/export/{galaxy_id}")
async def galaxies_export(
    galagxy_id: str, body: ExportGalaxyBody, db: Session = Depends(get_db)
) -> ExportGalaxyResponse:
    return ExportGalaxyResponse()


@router.post("/attachCluster/{attachTarget_id}/{attachTargetType}/local:{local}")
async def galaxies_attachCluster(
    attachTarget_id: str,
    attachTargetType: str,
    local: int,
    body: AttachClusterGalaxyBody,
    db: Session = Depends(get_db),
) -> AttachClusterGalaxyResponse:
    return AttachClusterGalaxyResponse()
