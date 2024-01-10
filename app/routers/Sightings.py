from fastapi import APIRouter, Depends  # , HTTPException
from sqlalchemy.orm import Session

# from ..models.sighting import Sighting
from ..database import get_db
from ..schemas.sightings.create_sighting_body import SightingCreateBody
from ..schemas.sightings.delete_sighting_response import SightingDeleteResponse
from ..schemas.sightings.get_sighting_response import SightingGetResponse

router = APIRouter(prefix="/sightings", tags=["sightings"])


@router.get("/")  # new
async def get_sightings(db: Session = Depends(get_db)) -> list[SightingGetResponse]:
    return []


@router.get("/index/{eventId}")
async def get_sightings_at_index(
    event_id: str, db: Session = Depends(get_db)
) -> SightingGetResponse:
    return SightingGetResponse(root=[])


@router.post("/add", deprecated=True)  # deprecated
@router.post("/")  # new
async def add_sighting(
    body: SightingCreateBody, db: Session = Depends(get_db)
) -> SightingGetResponse:
    return SightingGetResponse(root=[])


@router.post("/add/{attributeId}", deprecated=True)  # deprecated
@router.post("/{attributeId}")  # new
async def add_sightings_at_index(
    attribute_id: str, db: Session = Depends(get_db)
) -> SightingGetResponse:
    return SightingGetResponse(root=[])


@router.post("/delete/{sightingId}", deprecated=True)  # deprecated
@router.post("/{sightingId}")  # new
async def delete_sighting(
    sighting_id: str, db: Session = Depends(get_db)
) -> SightingDeleteResponse:
    return SightingDeleteResponse(
        saved=False, success=False, name="", message="", url=""
    )
