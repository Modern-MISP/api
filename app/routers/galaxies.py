from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.galaxy import Galaxy
# from ..schemas.galaxy_schema import GalaxySchema

router = APIRouter(prefix="/galaxies", tags=["galaxies"])


# -- Delete


@router.delete("/delete/{galaxyId}")
@router.delete("/{galaxyId}")
async def galaxies_delete(db: Session = Depends(get_db)) -> str:
    return ""


# -- Get


@router.get("/")
async def galaxies_get(db: Session = Depends(get_db)) -> List[Galaxy]:
    return []


@router.get("/view/{galaxyId}")
@router.get("/{galaxyId}")
async def galaxies_getById(db: Session = Depends(get_db)) -> Galaxy:
    return Galaxy


# -- Post


@router.post("")
async def galaxies_post(db: Session = Depends(get_db)) -> List[Galaxy]:
    return []


@router.post("/update")
async def galaxies_update(db: Session = Depends(get_db)) -> str:
    return ""


# import GalaxyClusterSchema and Galaxy
@router.post("/import")
async def galaxies_import(db: Session = Depends(get_db)):  # -> List[GalaxyCluster]
    return ""


@router.post("/export/{galaxyId}")
async def galaxies_export(db: Session = Depends(get_db)):  # -> GalaxyCluster:
    return ""


@router.post("/attachCluster/{attachTargetId}/{attachTargetType}/local:{local}")
async def galaxies_attachCluster(db: Session = Depends(get_db)) -> str:
    return ""
