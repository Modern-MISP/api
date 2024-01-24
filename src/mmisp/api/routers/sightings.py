from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from mmisp.api_schemas.sightings.create_sighting_body import SightingCreateBody
from mmisp.api_schemas.sightings.delete_sighting_response import SightingDeleteResponse
from mmisp.api_schemas.sightings.get_sighting_response import SightingGetResponse

# from ..models.sighting import Sighting
from mmisp.db.database import get_db

router = APIRouter(prefix="/sightings", tags=["sightings"])


@router.get("/", summary="Get all sightings", description="Retrieve a list of all sightings.")
async def get_sightings(db: Session = Depends(get_db)) -> list[SightingGetResponse]:
    # Logic to get sightings goes here

    return []


@router.get(
    "/index/{eventId}",
    summary="Get sightings for event",
    description="Retrieve all sightings associated with a specific event ID.",
)
async def get_sightings_at_index(event_id: str, db: Session = Depends(get_db)) -> SightingGetResponse:
    # Logic to get sightings for an event goes here

    return SightingGetResponse(root=[])


@router.post(
    "/add",
    deprecated=True,
    summary="Add sighting (Deprecated)",
    description="Deprecated. Add a new sighting using the old route.",
)
@router.post("/", summary="Add sighting", description="Add a new sighting.")
async def add_sighting(body: SightingCreateBody, db: Session = Depends(get_db)) -> SightingGetResponse:
    # Logic to add a new sighting goes here

    return SightingGetResponse(root=[])


@router.post(
    "/add/{attributeId}",
    deprecated=True,
    summary="Add sighting at index (Deprecated)",
    description="Deprecated. Add a new sighting for a specific attribute using the old route.",
)
@router.post(
    "/{attributeId}", summary="Add sighting at index", description="Add a new sighting for a specific attribute."
)
async def add_sightings_at_index(
    attribute_id: str, body: SightingCreateBody, db: Session = Depends(get_db)
) -> SightingGetResponse:
    # Logic to add a sighting for an attribute goes here

    return SightingGetResponse(root=[])


@router.post(
    "/delete/{sightingId}",
    deprecated=True,
    summary="Delete sighting (Deprecated)",
    description="Deprecated. Delete a specific sighting using the old route.",
)
@router.delete("/{sightingId}", summary="Delete sighting", description="Delete a specific sighting.")
async def delete_sighting(sighting_id: str, db: Session = Depends(get_db)) -> SightingDeleteResponse:
    # Logic to delete a sighting goes here

    return SightingDeleteResponse(saved=False, success=False, name="", message="", url="")
