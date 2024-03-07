from time import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.sightings.create_sighting_body import SightingCreateBody, SightingFiltersBody
from mmisp.api_schemas.sightings.get_sighting_response import (
    SightingAttributesResponse,
    SightingOrganisationResponse,
    SightingsGetResponse,
)
from mmisp.api_schemas.standard_status_response import StandardStatusResponse
from mmisp.db.database import get_db, with_session_management
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.sighting import Sighting
from mmisp.util.partial import partial

router = APIRouter(tags=["sightings"])


@router.post(
    "/sightings",
    status_code=status.HTTP_201_CREATED,
    response_model=partial(SightingsGetResponse),
    summary="Add sighting",
    description="Add a new sighting.",
)
@with_session_management
async def add_sighting(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    body: SightingCreateBody,
) -> list[dict[str, Any]]:
    return await _add_sighting(db, body)


@router.post(
    "/sightings/{attributeId}",
    status_code=status.HTTP_201_CREATED,
    response_model=partial(SightingsGetResponse),
    summary="Add sighting at index",
    description="Add a new sighting for a specific attribute.",
)
@with_session_management
async def add_sightings_at_index(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int, Path(alias="attributeId")],
) -> dict[str, Any]:
    return await _add_sightings_at_index(db, attribute_id)


@router.get(
    "/sightings/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(SightingsGetResponse),
    summary="Get sightings for event",
    description="Retrieve all sightings associated with a specific event ID.",
)
@with_session_management
async def get_sightings_at_index(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[int, Path(alias="eventId")],
) -> dict[str, Any]:
    return await _get_sightings_at_index(db, event_id)


@router.delete(
    "/sightings/{sightingId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(StandardStatusResponse),
    summary="Delete sighting",
    description="Delete a specific sighting.",
)
@with_session_management
async def delete_sighting(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    sighting_id: Annotated[int, Path(alias="sightingId")],
) -> dict[str, Any]:
    return await _delete_sighting(db, sighting_id)


@router.get(
    "/sightings",
    status_code=status.HTTP_200_OK,
    response_model=partial(SightingsGetResponse),
    summary="Get all sightings",
    description="Retrieve a list of all sightings.",
)
@with_session_management
async def get_sightings(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict[str, Any]]:
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
@with_session_management
async def add_sighting_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    body: SightingCreateBody,
) -> list[dict[str, Any]]:
    return await _add_sighting(db, body)


@router.post(
    "/sightings/add/{attributeId}",
    deprecated=True,
    status_code=status.HTTP_201_CREATED,
    response_model=partial(SightingsGetResponse),
    summary="Add sighting at index (Deprecated)",
    description="Deprecated. Add a new sighting for a specific attribute using the old route.",
)
@with_session_management
async def add_sightings_at_index_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int, Path(alias="attributeId")],
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
@with_session_management
async def delete_sighting_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    sighting_id: Annotated[int, Path(alias="sightingId")],
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
@with_session_management
async def get_sightings_at_index_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[int, Path(alias="eventId")],
) -> dict[str, Any]:
    return await _get_sightings_at_index(db, event_id)


# --- endpoint logic ---


async def _add_sighting(db: Session, body: SightingCreateBody) -> list[dict[str, Any]]:
    filters: SightingFiltersBody | None = body.filters.dict(exclude_unset=True) if body.filters else None
    responses: list[SightingsGetResponse] = []
    attributes: list[Attribute] = []

    if filters and body.filters.return_format is None:
        body.filters.return_format = "json"
    elif filters:
        _check_valid_return_format(return_format=body.filters.return_format)

    for value in body.values:
        value_specific_filters = {"value": value}
        if filters:
            value_specific_filters.update(filters)
            attributes = _build_query(db=db, filters=value_specific_filters)
        else:
            attributes = db.query(Attribute).filter(Attribute.value1 == value).all()

        if not attributes:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No Attributes with given values found.")

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
            db.flush()
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

    db.commit()

    return SightingsGetResponse(sightings=[response.__dict__ for response in responses])


async def _add_sightings_at_index(db: Session, attribute_id: int) -> dict[str, Any]:
    attribute: Attribute | None = db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Attribute not found.")

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

    return SightingsGetResponse(sightings=[response.__dict__])


async def _get_sightings_at_index(db: Session, event_id: int) -> dict[str, Any]:
    if not db.get(Event, event_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found.")

    sightings: list[Sighting] = db.query(Sighting).filter(Sighting.event_id == event_id).all()

    for sighting in sightings:
        organisation: Organisation = db.get(Organisation, sighting.org_id)

        organisation_response: SightingOrganisationResponse = SightingOrganisationResponse(
            id=organisation.id if organisation else None,
            uuid=organisation.uuid if organisation else None,
            name=organisation.name if organisation else None,
        )

        sighting.organisation = organisation_response.__dict__

    return SightingsGetResponse(sightings=[sighting.__dict__ for sighting in sightings])


async def _delete_sighting(db: Session, sighting_id: int) -> dict[str, Any]:
    sighting: Sighting | None = db.get(Sighting, sighting_id)

    if not sighting:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sighting not found.")

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
    return int(time())


def _check_valid_return_format(return_format: str) -> None:
    if return_format not in ["json"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid return format.")


def _build_query(db: Session, filters: SightingFiltersBody) -> list[Attribute]:
    search_body: SightingFiltersBody = SightingFiltersBody(**filters)
    query: Attribute = db.query(Attribute)

    if search_body.value1:
        query = query.filter(Attribute.value1 == search_body.value1)

    if search_body.value1:
        query = query.filter(Attribute.value1 == search_body.value1)

    if search_body.value2:
        query = query.filter(Attribute.value2 == search_body.value2)

    if search_body.type:
        query = query.filter(Attribute.type == search_body.type)

    if search_body.category:
        query = query.filter(Attribute.category == search_body.category)

    if search_body.from_:
        query = query.filter(Attribute.timestamp >= search_body.from_)

    if search_body.to:
        query = query.filter(Attribute.timestamp <= search_body.to)

    if search_body.last:
        query = query.filter(Attribute.last_seen > search_body.last)

    if search_body.timestamp:
        query = query.filter(Attribute.timestamp == search_body.timestamp)

    if search_body.event_id:
        query = query.filter(Attribute.event_id == search_body.event_id)

    if search_body.uuid:
        query = query.filter(Attribute.uuid == search_body.uuid)

    if search_body.timestamp:
        query = query.filter(Attribute.timestamp == search_body.attribute_timestamp)

    if search_body.to_ids:
        query = query.filter(Attribute.to_ids == search_body.to_ids)

    if search_body.deleted:
        query = query.filter(Attribute.deleted == search_body.deleted)

    if search_body.event_timestamp:
        events = db.query(Event).filter(Event.timestamp == search_body.event_timestamp).all()

        for event in events:
            query = query.filter(Attribute.event_id == event.id)

    if search_body.event_info:
        events = db.query(Event).filter(Event.info.like(f"%{search_body.event_info}%"))

        for event in events:
            query = query.filter(Attribute.event_id == event.id)

    if search_body.sharing_group:
        for sharing_group in search_body.sharing_group:
            query = query.filter(Attribute.sharing_group_id == sharing_group)

    if search_body.first_seen:
        query = query.filter(Attribute.first_seen == search_body.first_seen)

    if search_body.last_seen:
        query = query.filter(Attribute.last_seen == search_body.last_seen)

    if search_body.requested_attributes:
        for attribute in search_body.requested_attributes:
            query = query.filter(Attribute.id == attribute)

    if search_body.limit:
        query = query.limit(int(search_body.limit))

    return query.all()
