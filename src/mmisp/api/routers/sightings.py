import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.sightings.create_sighting_body import SightingCreateBody
from mmisp.api_schemas.sightings.get_sighting_response import (
    SightingAttributesResponse,
    SightingGetResponse,
    SightingOrganisationResponse,
    SightingsGetResponse,
)
from mmisp.api_schemas.standard_status_response import StandardStatusResponse
from mmisp.db.database import get_db
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.sighting import Sighting
from mmisp.util.partial import partial
from mmisp.util.request_validations import check_existence_and_raise

router = APIRouter(tags=["sightings"])


# Sorted according to CRUD


@router.post(
    "/sightings",
    status_code=status.HTTP_201_CREATED,
    response_model=partial(SightingsGetResponse),
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
) -> dict[str, Any]:
    return await _add_sightings_at_index(db, attribute_id)


@router.get(
    "/sightings/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(SightingsGetResponse),
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
    response_model=partial(StandardStatusResponse),
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
    response_model=partial(SightingsGetResponse),
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
    response_model=partial(SightingsGetResponse),
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
) -> dict[str, Any]:
    return await _add_sightings_at_index(db, attribute_id)


@router.post(
    "/sightings/delete/{sightingId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(StandardStatusResponse),
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
    response_model=partial(SightingsGetResponse),
    summary="Get sightings for event (Deprecated)",
    description="Deprecated. Retrieve all sightings associated with a specific event ID using the old route.",
)
async def get_sightings_at_index_depr(
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
) -> dict[str, Any]:
    return await _get_sightings_at_index(db, event_id)


# --- endpoint logic ---


async def _add_sighting(db: Session, body: SightingCreateBody) -> list[dict[str, Any]]:
    responses: list[SightingsGetResponse] = []

    for value in body.values:
        attributes: list[Attribute] = db.query(Attribute).filter(Attribute.value == value).all()

        for attribute in attributes:
            sighting: Sighting = Sighting(
                attribute_id=int(attribute.id),
                event_id=int(attribute.event_id),
                org_id=int(db.get(Event, attribute.event_id).org_id),
                date_sighting=_create_timestamp(),
                source=body.source if body.source else None,
                type=int(body.filters.type) if body.filters and body.filters.type else None,
            )
            db.add(sighting)
            db.commit()
            db.refresh(sighting)

            organisation: Organisation = db.get(Organisation, sighting.org_id)

            organisation_response: SightingOrganisationResponse = SightingOrganisationResponse(
                id=organisation.id if organisation else None,
                uuid=organisation.uuid if organisation else None,
                name=organisation.name if organisation else None,
            )

            responses.append(
                SightingAttributesResponse(
                    **sighting.__dict__,
                    organisation=organisation_response,
                )
            )

    return SightingsGetResponse(sightings=[response.__dict__ for response in responses])


async def _add_sightings_at_index(db: Session, attribute_id: str) -> dict[str, Any]:
    attribute: Attribute = check_existence_and_raise(
        db=db, model=Attribute, value=attribute_id, column_name="id", error_detail="Attribute not found."
    )

    sighting: Sighting = Sighting(
        attribute_id=int(attribute_id),
        event_id=int(attribute.event_id),
        org_id=int(db.get(Event, attribute.event_id).org_id),
        date_sighting=_create_timestamp(),
    )
    db.add(sighting)
    db.commit()
    db.refresh(sighting)

    organisation: Organisation = db.get(Organisation, sighting.org_id)

    organisation_response: SightingOrganisationResponse = SightingOrganisationResponse(
        id=organisation.id if organisation else None,
        uuid=organisation.uuid if organisation else None,
        name=organisation.name if organisation else None,
    )
    response: SightingAttributesResponse = SightingAttributesResponse(
        **sighting.__dict__,
        organisation=organisation_response,
    )

    return SightingGetResponse(sighting=response.__dict__)


async def _get_sightings_at_index(db: Session, event_id: str) -> dict[str, Any]:
    check_existence_and_raise(db=db, model=Event, value=event_id, column_name="id", error_detail="Event not found.")
    sightings: list[Sighting] = db.query(Sighting).filter(Sighting.event_id == event_id).all()

    return SightingsGetResponse(sightings=[sighting.__dict__ for sighting in sightings])


async def _delete_sighting(db: Session, sighting_id: str) -> dict[str, Any]:
    sighting: Sighting = check_existence_and_raise(
        db=db, model=Sighting, value=sighting_id, column_name="id", error_detail="Sighting not found."
    )
    db.delete(sighting)
    db.commit()
    saved: bool = True
    success: bool = True
    message: str = "Sighting successfully deleted."

    return StandardStatusResponse(
        saved=saved,
        success=success,
        name=message,
        message=message,
        url=f"/objects/{sighting_id}",
    )


async def _get_sightings(db: Session) -> list[dict[str, Any]]:
    responses: list[SightingsGetResponse] = []
    sightings: list[Sighting] = db.query(Sighting).all()

    if not sightings:
        return SightingsGetResponse(sightings=[])

    for sighting in sightings:
        organisation: Organisation = db.get(Organisation, sighting.org_id)

        organisation_response: SightingOrganisationResponse = SightingOrganisationResponse(
            id=organisation.id if organisation else None,
            uuid=organisation.uuid if organisation else None,
            name=organisation.name if organisation else None,
        )

        responses.append(
            SightingAttributesResponse(
                **sighting.__dict__,
                organisation=organisation_response,
            )
        )

    return SightingsGetResponse(sightings=[response.__dict__ for response in responses])


def _create_timestamp() -> int:
    return int(time.time())
