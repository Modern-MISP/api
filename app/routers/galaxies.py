from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.galaxies.delete_galaxy_response import GalaxyDeleteResponse
from ..schemas.galaxies.get_all_galaxies import GalaxiesGetResponse
from ..schemas.galaxies.get_galaxy_response import GalaxyGetResponse
from ..schemas.galaxies.search_galaxies_body import GalaxySearchBody
from ..schemas.galaxies.search_galaxies_response import GalaxySearchResponse
from ..schemas.galaxies.forece_update_galaxies_response import GalaxyUpdateResponse
from ..schemas.galaxies.import_galaxies_body import GalaxyImportBody
from ..schemas.galaxies.import_galaxies_response import GalaxyImportResponse
from ..schemas.galaxies.export_galaxies_body import GalaxyExportBody
from ..schemas.galaxies.export_galaxies_response import GalaxyExportResponse
from ..schemas.galaxies.attach_galaxy_cluster_body import GalaxyAttachClusterBody
from ..schemas.galaxies.attach_galaxy_cluster_response import (
    GalaxyAttachClusterResponse,
)

router = APIRouter(prefix="/galaxies", tags=["galaxies"])


# -- Delete


@router.delete("/delete/{galaxy_id}", deprecated=True)  # deprecated
@router.delete("/{galaxy_id}")  # new
async def galaxies_delete(
    galagxy_id: str, db: Session = Depends(get_db)
) -> GalaxyDeleteResponse:
    return GalaxyDeleteResponse


# -- Get


@router.get("/")
async def galaxies_get(db: Session = Depends(get_db)) -> GalaxiesGetResponse:
    return GalaxiesGetResponse


@router.get("/view/{galaxy_id}", deprecated=True)  # deprecated
@router.get("/{galaxy_id}")  # new
async def galaxies_getById(db: Session = Depends(get_db)) -> GalaxyGetResponse:
    return GalaxyGetResponse


# -- Post


@router.post("")
async def galaxies_post(
    body: GalaxySearchBody, db: Session = Depends(get_db)
) -> GalaxySearchResponse:
    return GalaxySearchResponse


@router.post("/update")
async def galaxies_update(db: Session = Depends(get_db)) -> GalaxyUpdateResponse:
    return GalaxyUpdateResponse


@router.post("/import")
async def galaxies_import(
    body: GalaxyImportBody, db: Session = Depends(get_db)
) -> GalaxyImportResponse:
    return GalaxyImportResponse


@router.post("/export/{galaxy_id}")
async def galaxies_export(
    galagxy_id: str, body: GalaxyExportBody, db: Session = Depends(get_db)
) -> GalaxyExportResponse:
    return GalaxyExportResponse


@router.post("/attachCluster/{attachTarget_id}/{attachTargetType}/local:{local}")
async def galaxies_attachCluster(
    attachTarget_id: str,
    attachTargetType: str,
    local: int,
    body: GalaxyAttachClusterBody,
    db: Session = Depends(get_db),
) -> GalaxyAttachClusterResponse:
    return GalaxyAttachClusterResponse
