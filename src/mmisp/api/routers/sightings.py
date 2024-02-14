import logging
from typing import Annotated, Any

# from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi import APIRouter, Depends, Path, status

# from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.sightings.create_sighting_body import SightingCreateBody
from mmisp.api_schemas.sightings.delete_sighting_response import SightingDeleteResponse
from mmisp.api_schemas.sightings.get_sighting_response import SightingGetResponse
from mmisp.db.database import get_db

# from mmisp.db.models.sighting import Sighting
from mmisp.util.partial import partial

# from mmisp.util.request_validations import check_existence_and_raise

router = APIRouter(tags=["sightings"])
logging.basicConfig(level=logging.INFO)

info_format = "%(asctime)s - %(message)s"
error_format = "%(asctime)s - %(filename)s:%(lineno)d - %(message)s"

info_handler = logging.StreamHandler()
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter(info_format))

error_handler = logging.StreamHandler()
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(error_format))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(info_handler)
logger.addHandler(error_handler)


# Sorted according to CRUD


@router.post(
    "/sightings",
    status_code=status.HTTP_201_CREATED,
    response_model=partial(SightingGetResponse),
    summary="Add sighting",
    description="Add a new sighting.",
)
async def add_sighting(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    body: SightingCreateBody,
) -> list[dict[str, Any]]:
    return await _add_sighting(db, body)


@router.post(
    "/sightings/{attributeId}",
    status_code=status.HTTP_201_CREATED,
    response_model=partial(SightingGetResponse),
    summary="Add sighting at index",
    description="Add a new sighting for a specific attribute.",
)
async def add_sightings_at_index(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(..., alias="attributeId")],
    body: SightingCreateBody,
) -> dict[str, Any]:
    return await _add_sightings_at_index(db, attribute_id, body)


@router.get(
    "/sightings/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(SightingGetResponse),
    summary="Get sightings for event",
    description="Retrieve all sightings associated with a specific event ID.",
)
async def get_sightings_at_index(
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
) -> dict[str, Any]:
    return await _get_sightings_at_index(db, event_id)


@router.delete(
    "/sightings/{sightingId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(SightingDeleteResponse),
    summary="Delete sighting",
    description="Delete a specific sighting.",
)
async def delete_sighting(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    sighting_id: Annotated[str, Path(..., alias="sightingId")],
) -> dict[str, Any]:
    return await _delete_sighting(db, sighting_id)


@router.get(
    "/sightings",
    status_code=status.HTTP_200_OK,
    response_model=partial(SightingGetResponse),
    summary="Get all sightings",
    description="Retrieve a list of all sightings.",
)
async def get_sightings(db: Annotated[Session, Depends(get_db)]) -> list[dict[str, Any]]:
    return await _get_sightings(db)


# --- deprecated ---


@router.post(
    "/sightings/add",
    deprecated=True,
    status_code=status.HTTP_201_CREATED,
    response_model=partial(SightingGetResponse),
    summary="Add sighting (Deprecated)",
    description="Deprecated. Add a new sighting using the old route.",
)
async def add_sighting_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    body: SightingCreateBody,
) -> list[dict[str, Any]]:
    return await _add_sighting(db, body)


@router.post(
    "/sightings/add/{attributeId}",
    deprecated=True,
    status_code=status.HTTP_201_CREATED,
    response_model=partial(SightingGetResponse),
    summary="Add sighting at index (Deprecated)",
    description="Deprecated. Add a new sighting for a specific attribute using the old route.",
)
async def add_sightings_at_index_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(..., alias="attributeId")],
    body: SightingCreateBody,
) -> dict[str, Any]:
    return await _add_sightings_at_index(db, attribute_id, body)


@router.post(
    "/sightings/delete/{sightingId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(SightingDeleteResponse),
    summary="Delete sighting (Deprecated)",
    description="Deprecated. Delete a specific sighting using the old route.",
)
async def delete_sighting_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    sighting_id: Annotated[str, Path(..., alias="sightingId")],
) -> dict[str, Any]:
    return await _delete_sighting(db, sighting_id)


@router.get(
    "/sightings/index/{eventId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(SightingGetResponse),
    summary="Get sightings for event (Deprecated)",
    description="Deprecated. Retrieve all sightings associated with a specific event ID using the old route.",
)
async def get_sightings_at_index_depr(
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
) -> dict[str, Any]:
    return await _get_sightings_at_index(db, event_id)


# --- endpoint logic ---


async def _add_sighting(
    db: Session,
    body: SightingCreateBody,
) -> list[dict[str, Any]]:
    return [{"key": "hold"}]


async def _add_sightings_at_index(
    db: Session,
    attribute_id: str,
    body: SightingCreateBody,
) -> dict[str, Any]:
    return {"key": "hold"}


async def _get_sightings_at_index(
    db: Session,
    event_id: str,
) -> dict[str, Any]:
    return {"key": "hold"}


async def _delete_sighting(
    db: Session,
    sighting_id: str,
) -> dict[str, Any]:
    return {"key": "hold"}


async def _get_sightings(db: Session) -> list[dict[str, Any]]:
    return [{"key": "hold"}]
