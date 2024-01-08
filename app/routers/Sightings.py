from typing import List

from fastapi import APIRouter, Depends  # , HTTPException
from sqlalchemy.orm import Session

from ..database import get_db

# from ..models.sighting import Sighting
from ..schemas.sighting_schema import SightingDeleteSchema, SightingSchema

router = APIRouter(prefix="/sightings")


@router.get("/", response_model=List[SightingSchema])
async def get_sightings(db: Session = Depends(get_db)) -> None:
    pass


@router.get("/index/{eventId}", response_model=List[SightingSchema])
async def get_sightings_at_index(event_id: str, db: Session = Depends(get_db)) -> None:
    pass


@router.post("/add", response_model=List[SightingSchema])
@router.post("/", response_model=List[SightingSchema])
async def add_sighting(db: Session = Depends(get_db)) -> None:
    pass


@router.post("/add/{attributeId}", response_model=List[SightingSchema])
@router.post("/{attributeId}", response_model=List[SightingSchema])
async def add_sightings_at_index(
    attribute_id: str, db: Session = Depends(get_db)
) -> None:
    pass


@router.post("/delete/{sightingId}", response_model=List[SightingDeleteSchema])
@router.post("/{sightingId}", response_model=List[SightingDeleteSchema])
async def delete_sighting(sighting_id: str, db: Session = Depends(get_db)) -> None:
    pass
