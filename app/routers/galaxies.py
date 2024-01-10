from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.galaxy import Galaxy
from ..schemas.galaxy_schema import GalaxySchema

router = APIRouter(prefix="/galaxies")


@router.get("", response_model=List[GalaxySchema])
async def galaxies_get(db: Session = Depends(get_db)) -> List[Galaxy]:
    pass


@router.post("", response_model=List[GalaxySchema])
async def galaxies_post(db: Session = Depends(get_db)) -> List[Galaxy]:
    pass


@router.get("/view/{galaxyId}", response_model=GalaxySchema)
@router.get("/{galaxyId}", response_model=GalaxySchema)
async def galaxies_getById(db: Session = Depends(get_db)) -> Galaxy:
    pass


@router.post("/update", response_model=str)
async def galaxies_update(db: Session = Depends(get_db)) -> str:
    pass


@router.delete("/delete/{galaxyId}", response_model=str)
@router.delete("/{galaxyId}")
async def galaxies_delete(db: Session = Depends(get_db)) -> str:
    pass


# import GalaxyClusterSchema and Galaxy
@router.post("/import")  # , response_model=List[GalaxyClusterSchema]
async def galaxies_import(db: Session = Depends(get_db)):  # -> List[GalaxyCluster]
    pass


@router.post("/export/{galaxyId}")  # , response_model=GalaxyClusterSchema
async def galaxies_export(db: Session = Depends(get_db)):  # -> GalaxyCluster:
    pass


@router.post(
    "/attachCluster/{attachTargetId}/{attachTargetType}/local:{local}",
    response_model=str,
)
async def galaxies_attachCluster(db: Session = Depends(get_db)) -> str:
    pass
