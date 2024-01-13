from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.galaxies.delete_force_update_import_galaxy_response import (
    DeleteForceUpdateImportGalaxyResponse,
)
from ..schemas.galaxies.get_all_search_galaxies_response import (
    GetAllSearchGalaxiesResponse,
)
from ..schemas.galaxies.get_galaxy_response import GetGalaxyResponse
from ..schemas.galaxies.search_galaxies_body import SearchGalaxiesBody
from ..schemas.galaxies.import_galaxies_body import ImportGalaxyBody
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
) -> DeleteForceUpdateImportGalaxyResponse:
    return DeleteForceUpdateImportGalaxyResponse()


# -- Get


@router.get("/")
async def galaxies_get(
    db: Session = Depends(get_db),
) -> list[GetAllSearchGalaxiesResponse]:
    return list[GetAllSearchGalaxiesResponse()]


@router.get("/view/{galaxy_id}", deprecated=True)  # deprecated
@router.get("/{galaxy_id}")  # new
async def galaxies_getById(db: Session = Depends(get_db)) -> GetGalaxyResponse:
    return GetGalaxyResponse()


# -- Post


@router.post("/")
async def galaxies_post(
    body: SearchGalaxiesBody, db: Session = Depends(get_db)
) -> list[GetAllSearchGalaxiesResponse]:
    return list[GetAllSearchGalaxiesResponse()]


@router.post("/update")
async def galaxies_update(
    db: Session = Depends(get_db),
) -> DeleteForceUpdateImportGalaxyResponse:
    return DeleteForceUpdateImportGalaxyResponse


@router.post("/import")
async def galaxies_import(
    body: list[ImportGalaxyBody], db: Session = Depends(get_db)
) -> DeleteForceUpdateImportGalaxyResponse:
    return DeleteForceUpdateImportGalaxyResponse()


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
