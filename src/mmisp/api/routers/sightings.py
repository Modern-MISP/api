import uuid
from collections.abc import Sequence
from time import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import and_, select
from sqlalchemy.sql.expression import Select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.responses.standard_status_response import StandardStatusResponse
from mmisp.api_schemas.sightings import (
    SightingAttributesResponse,
    SightingCreateBody,
    SightingFiltersBody,
    SightingOrganisationResponse,
    SightingsGetResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.sighting import Sighting
from mmisp.lib.logger import alog, log

from ..workflow import execute_workflow

router = APIRouter(tags=["sightings"])


@router.post(
    "/sightings",
    status_code=status.HTTP_201_CREATED,
    summary="Add sighting",
)
@alog
async def add_sighting(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    body: SightingCreateBody,
) -> list[SightingAttributesResponse]:
    """Add a new sighting for each given value.

    args:
        auth: Authentication details
        db: Database session
        body: Sighting creation data

    returns:
        details of the new sighting
    """
    return await _add_sighting(db, body)


@router.post(
    "/sightings/{attributeId}",
    status_code=status.HTTP_201_CREATED,
    summary="Add sighting at index",
)
@alog
async def add_sightings_at_index(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int | uuid.UUID, Path(alias="attributeId")],
) -> SightingAttributesResponse:
    """Add a new sighting for a specific attribute.

    args:
        auth: Authentication
        db: Database session
        attribute_id: ID or UUID of the attribute

    returns:
        details of new sightings
    """
    return await _add_sightings_at_index(db, attribute_id)


@router.get(
    "/sightings/{eventId}",
    status_code=status.HTTP_200_OK,
    summary="Get sightings for event",
)
@alog
async def get_sightings_at_index(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[int | uuid.UUID, Path(alias="eventId")],
) -> list[SightingAttributesResponse]:
    """Retrieve all sightings associated with a specific event ID or UUID.

    args:
        auth: Authentication
        db: Database session
        event_id: ID or UUID of the event

    returns:
        details of the sightings at index
    """
    return await _get_sightings_at_index(db, event_id)


@router.delete(
    "/sightings/{sightingId}",
    status_code=status.HTTP_200_OK,
    summary="Delete sighting",
)
@alog
async def delete_sighting(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    sighting_id: Annotated[int, Path(alias="sightingId")],
) -> StandardStatusResponse:
    """Delete a specific sighting.

    args:

    - auth: Authentication details

    - db: Database session

    - sighting_id: ID of the sighting

    returns:

    - Status response indicating success or failure
    """
    return await _delete_sighting(db, sighting_id)


@router.get(
    "/sightings",
    status_code=status.HTTP_200_OK,
    summary="Get all sightings",
)
@alog
async def get_sightings(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> SightingsGetResponse:
    """Retrieve a list of all sightings.

    args:

    - auth: Authentication details

    - db: Database session

    returns:

    - Status response indicating success or failure
    """
    return await _get_sightings(db)


# --- deprecated ---


@router.post(
    "/sightings/add",
    deprecated=True,
    status_code=status.HTTP_201_CREATED,
    summary="Add sighting (Deprecated)",
)
@alog
async def add_sighting_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    body: SightingCreateBody,
) -> list[SightingAttributesResponse]:
    """Deprecated. Add a new sighting using the old route.

    args:

    - auth: Authentication details

    - db: Database session

    - body: Sighting creation data

    returns:

    - List of sighting attributes
    """
    return await _add_sighting(db, body)


@router.post(
    "/sightings/add/{attributeId}",
    deprecated=True,
    status_code=status.HTTP_201_CREATED,
    summary="Add sighting at index (Deprecated)",
)
@alog
async def add_sightings_at_index_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int, Path(alias="attributeId")],
) -> SightingAttributesResponse:
    """Deprecated. Add a new sighting for a specific attribute using the old route.

    args:

    - auth: Authentication details

    - db: Database session

    - attribute_id: ID of the attribute

    returns:

    - Details of the new sightings
    """
    return await _add_sightings_at_index(db, attribute_id)


@router.post(
    "/sightings/delete/{sightingId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    summary="Delete sighting (Deprecated)",
)
@alog
async def delete_sighting_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SIGHTING]))],
    db: Annotated[Session, Depends(get_db)],
    sighting_id: Annotated[int, Path(alias="sightingId")],
) -> StandardStatusResponse:
    """Deprecated. Delete a specific sighting, using the old route.

    args:

    - auth: Authentication details

    - db: Database session

    - sighting_id: ID of the sighting

    returns:

    - Status response indicating success or failure
    """
    return await _delete_sighting(db, sighting_id)


@router.get(
    "/sightings/index/{eventId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    summary="Get sightings for event (Deprecated)",
)
@alog
async def get_sightings_at_index_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[int, Path(alias="eventId")],
) -> list[SightingAttributesResponse]:
    """Deprecated. Retrieve all sightings associated with a specific event ID using the old route.

    args:

    - auth: Authentication details

    - db: Database session

    - event_id: ID of the event

    returns:

    - Details of the sightings at index
    """
    return await _get_sightings_at_index(db, event_id)


# --- endpoint logic ---


@alog
async def _add_sighting(db: Session, body: SightingCreateBody) -> list[SightingAttributesResponse]:
    filters: SightingFiltersBody | None = body.filters if body.filters else None
    responses: list[SightingAttributesResponse] = []
    attributes: Sequence[Attribute] = []
    counter = len(body.values) - 1

    if filters and filters.returnFormat:
        _check_valid_return_format(return_format=filters.returnFormat)

    for value in body.values:
        if filters:
            attributes = await _get_attributes_with_filters(db=db, filters=filters, value=value)
        else:
            result = await db.execute(select(Attribute).filter(Attribute.value1 == value))
            attributes = result.scalars().all()

        if not attributes and counter == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No Attributes with given values found.")

        for attribute in attributes:
            event = await db.get(Event, attribute.event_id)
            if event is None:
                continue
            sighting: Sighting = Sighting(
                attribute_id=int(attribute.id),
                event_id=int(attribute.event_id),
                org_id=int(event.org_id),
                date_sighting=int(time()),
                source=body.source if body.source else None,
                type=int(filters.type) if filters and filters.type else None,
            )

            db.add(sighting)
            await db.flush()
            await db.refresh(sighting)
            await execute_workflow("sighting-after-save", db, attribute)

            organisation: Organisation | None = await db.get(Organisation, sighting.org_id)

            organisation_response: SightingOrganisationResponse = SightingOrganisationResponse(
                id=organisation.id if organisation else None,
                uuid=organisation.uuid if organisation else None,
                name=organisation.name if organisation else None,
            )

            responses.append(
                SightingAttributesResponse(
                    **sighting.__dict__,
                    attribute_uuid=attribute.uuid,
                    organisation=organisation_response,
                )
            )

        counter -= 1

    await db.flush()

    return responses


@alog
async def _add_sightings_at_index(db: Session, attribute_id: int | uuid.UUID) -> SightingAttributesResponse:
    qry = select(Attribute)
    if isinstance(attribute_id, uuid.UUID):
        qry = qry.filter(Attribute.uuid == attribute_id)
    else:
        qry = qry.filter(Attribute.id == attribute_id)

    result = await db.execute(qry)
    attribute = result.scalars().one_or_none()

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Attribute not found.")

    event = await db.get(Event, attribute.event_id)

    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found.")

    sighting: Sighting = Sighting(
        attribute_id=int(attribute.id),
        event_id=int(attribute.event_id),
        org_id=int(event.org_id),
        date_sighting=int(time()),
    )

    db.add(sighting)
    await db.flush()
    await db.refresh(sighting)
    await execute_workflow("sighting-after-save", db, attribute)

    organisation: Organisation | None = await db.get(Organisation, sighting.org_id)

    organisation_response: SightingOrganisationResponse = SightingOrganisationResponse(
        id=organisation.id if organisation else None,
        uuid=organisation.uuid if organisation else None,
        name=organisation.name if organisation else None,
    )
    response: SightingAttributesResponse = SightingAttributesResponse(
        **sighting.__dict__,
        attribute_uuid=attribute.uuid,
        organisation=organisation_response,
    )

    return response


@alog
async def _get_sightings_at_index(db: Session, event_id: int | uuid.UUID) -> list[SightingAttributesResponse]:
    qry = select(Event)
    if isinstance(event_id, uuid.UUID):
        qry = qry.filter(Event.uuid == event_id)
    else:
        qry = qry.filter(Event.id == event_id)

    result = await db.execute(qry)
    event = result.scalars().one_or_none()

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found.")

    result = await db.execute(select(Sighting).filter(Sighting.event_id == event.id))
    sightings: Sequence[Sighting] = result.scalars().all()

    for sighting in sightings:
        organisation: Organisation | None = await db.get(Organisation, sighting.org_id)

        organisation_response: SightingOrganisationResponse = SightingOrganisationResponse(
            id=organisation.id if organisation else None,
            uuid=organisation.uuid if organisation else None,
            name=organisation.name if organisation else None,
        )

        sighting.organisation = organisation_response.__dict__

    return [SightingAttributesResponse(**sighting.__dict__) for sighting in sightings]


@alog
async def _delete_sighting(db: Session, sighting_id: int) -> StandardStatusResponse:
    sighting: Sighting | None = await db.get(Sighting, sighting_id)

    if not sighting:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sighting not found.")

    await db.delete(sighting)
    await db.flush()
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


@alog
async def _get_sightings(db: Session) -> SightingsGetResponse:
    responses: list[SightingAttributesResponse] = []
    result = await db.execute(select(Sighting))
    sightings: Sequence[Sighting] = result.scalars().all()

    if not sightings:
        return SightingsGetResponse(sightings=[])

    attribute_ids = {sighting.attribute_id for sighting in sightings}
    org_ids = {sighting.org_id for sighting in sightings}

    attributes_result = await db.execute(select(Attribute).filter(Attribute.id.in_(attribute_ids)))
    attributes = attributes_result.scalars().all()
    organisations_result = await db.execute(select(Organisation).filter(Organisation.id.in_(org_ids)))
    organisations = organisations_result.scalars().all()

    attributes_by_id = {attribute.id: attribute for attribute in attributes}
    organisations_by_id = {organisation.id: organisation for organisation in organisations}

    responses = []
    for sighting in sightings:
        attribute = attributes_by_id.get(sighting.attribute_id)
        organisation = organisations_by_id.get(sighting.org_id)

        organisation_response = SightingOrganisationResponse(
            id=organisation.id if organisation else None,
            uuid=organisation.uuid if organisation else None,
            name=organisation.name if organisation else None,
        )

        responses.append(
            SightingAttributesResponse(
                **sighting.__dict__,
                attribute_uuid=attribute.uuid if attribute else None,
                organisation=organisation_response,
            )
        )

    return SightingsGetResponse(sightings=responses)


@log
def _check_valid_return_format(return_format: str) -> None:
    if return_format not in ["json"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid return format.")


@alog
async def _get_attributes_with_filters(db: Session, filters: SightingFiltersBody, value: str) -> Sequence[Attribute]:
    search_body: SightingFiltersBody = filters
    query: Select = select(Attribute)

    if search_body.value1:
        query = query.filter(and_(Attribute.value1 == search_body.value1, Attribute.value1 == value))

    if search_body.value2:
        query = query.filter(and_(Attribute.value2 == search_body.value2, Attribute.value1 == value))

    if search_body.type:
        query = query.filter(and_(Attribute.type == search_body.type, Attribute.value1 == value))

    if search_body.category:
        query = query.filter(and_(Attribute.category == search_body.category, Attribute.value1 == value))

    if search_body.from_:
        query = query.filter(and_(Attribute.timestamp >= search_body.from_, Attribute.value1 == value))

    if search_body.to:
        query = query.filter(and_(Attribute.timestamp <= search_body.to, Attribute.value1 == value))

    if search_body.last:
        query = query.filter(and_(Attribute.last_seen > search_body.last, Attribute.value1 == value))

    if search_body.timestamp:
        query = query.filter(and_(Attribute.timestamp == search_body.timestamp, Attribute.value1 == value))

    if search_body.event_id:
        query = query.filter(and_(Attribute.event_id == search_body.event_id, Attribute.value1 == value))

    if search_body.uuid:
        query = query.filter(and_(Attribute.uuid == search_body.uuid, Attribute.value1 == value))

    if search_body.timestamp:
        query = query.filter(and_(Attribute.timestamp == search_body.attribute_timestamp, Attribute.value1 == value))

    if search_body.to_ids:
        query = query.filter(and_(Attribute.to_ids == search_body.to_ids, Attribute.value1 == value))

    if search_body.deleted:
        query = query.filter(and_(Attribute.deleted == search_body.deleted, Attribute.value1 == value))

    if search_body.event_timestamp:
        subquery = select(Event.id).filter(
            and_(Event.timestamp == search_body.event_timestamp, Attribute.value1 == value)
        )
        query = query.filter(Attribute.event_id.in_(subquery))

    if search_body.eventinfo:
        subquery = select(Event.id).filter(
            and_(Event.info.like(f"%{search_body.eventinfo}%"), Attribute.value1 == value)
        )
        query = query.filter(Attribute.event_id.in_(subquery))

    if search_body.sharinggroup:
        query = query.filter(and_(Attribute.sharing_group_id.in_(search_body.sharinggroup), Attribute.value1 == value))

    if search_body.first_seen:
        query = query.filter(and_(Attribute.first_seen == search_body.first_seen, Attribute.value1 == value))

    if search_body.last_seen:
        query = query.filter(and_(Attribute.last_seen == search_body.last_seen, Attribute.value1 == value))

    if search_body.requested_attributes:
        query = query.filter(
            and_(Attribute.sharing_group_id.in_(search_body.requested_attributes), Attribute.value1 == value)
        )

    if search_body.limit:
        query = query.limit(int(search_body.limit))

    result = await db.execute(query)
    return result.scalars().all()
