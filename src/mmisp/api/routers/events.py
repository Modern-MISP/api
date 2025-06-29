import logging
import uuid
from collections import defaultdict
from collections.abc import Sequence
from datetime import date, datetime
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from starlette.requests import Request

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api.config import config
from mmisp.api_schemas.events import (
    AddEditGetEventAttribute,
    AddEditGetEventDetails,
    AddEditGetEventEventReport,
    AddEditGetEventGalaxy,
    AddEditGetEventGalaxyCluster,
    AddEditGetEventGalaxyClusterRelation,
    AddEditGetEventObject,
    AddEditGetEventOrg,
    AddEditGetEventResponse,
    AddEditGetEventTag,
    AddEventBody,
    AddRemoveTagEventsResponse,
    DeleteEventResponse,
    EditEventBody,
    GetAllEventsEventTag,
    GetAllEventsEventTagTag,
    GetAllEventsGalaxyCluster,
    GetAllEventsGalaxyClusterGalaxy,
    GetAllEventsOrg,
    GetAllEventsResponse,
    IndexEventsAttributes,
    IndexEventsBody,
    PublishEventResponse,
    SearchEventsBody,
    SearchEventsResponse,
    UnpublishEventResponse,
)
from mmisp.api_schemas.jobs import (
    AddAttributeViaFreeTextImportEventBody,
    FreeTextImportWorkerBody,
    FreeTextImportWorkerData,
    FreeTextImportWorkerUser,
)
from mmisp.api_schemas.sharing_groups import (
    EventSharingGroupResponse,
)
from mmisp.db.database import get_db
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.event import Event, EventReport, EventTag
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyReference
from mmisp.db.models.object import Object
from mmisp.db.models.sharing_group import SharingGroup, SharingGroupOrg
from mmisp.db.models.tag import Tag
from mmisp.db.models.user import User
from mmisp.lib.actions import action_publish_event
from mmisp.lib.galaxies import parse_galaxy_authors
from mmisp.lib.logger import alog, log

from ..workflow import execute_blocking_workflow, execute_workflow

logger = logging.getLogger("mmisp")

router = APIRouter(tags=["events"])


@router.post(
    "/events",
    status_code=status.HTTP_200_OK,
    summary="Add new event",
)
@alog
async def add_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.ADD]))],
    db: Annotated[AsyncSession, Depends(get_db)],
    body: AddEventBody,
) -> AddEditGetEventResponse:
    """Add a new event with the given details.

    args:
        auth: the user's authentification status
        db: the current database
        body: the request body

    returns:
        the new event
    """
    return await _add_event(auth, db, body)


@router.get(
    "/events/{eventId}",
    status_code=status.HTTP_200_OK,
    summary="Get event details",
)
@alog
async def get_event_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_id: Annotated[int | uuid.UUID, Path(alias="eventId")],
) -> AddEditGetEventResponse:
    """Retrieve details of a specific event either by its event ID, or via its UUID.

    args:
        auth: the user's authentification status
        db: the current database
        event_id: the ID or UUID of the event

    returns:
        the event details
    """
    return await _get_event_details(db, event_id, auth.user)


@router.put(
    "/events/{eventId}",
    status_code=status.HTTP_200_OK,
    summary="Update an event",
)
@alog
async def update_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_id: Annotated[int | uuid.UUID, Path(alias="eventId")],
    body: EditEventBody,
) -> AddEditGetEventResponse:
    """Update an existing event either by its event ID or via its UUID.

    args:
        auth: the user's authentification status
        db: the current database
        event_id: the ID or UUID of the event
        body: the request body

    returns:
        the updated event
    """
    return await _update_event(db, event_id, body, auth.user)


@router.delete(
    "/events/{eventId}",
    status_code=status.HTTP_200_OK,
    summary="Delete an event",
)
@alog
async def delete_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_id: Annotated[int | uuid.UUID, Path(alias="eventId")],
) -> DeleteEventResponse:
    """Delete an event either by its event ID or via its UUID.

    args:
        auth: the user's authentification status
        db: the current database
        event_id: the ID or UUID of the event

    returns:
        the deleted event
    """
    return await _delete_event(db, event_id, auth.user)


@router.get(
    "/events",
    status_code=status.HTTP_200_OK,
    summary="Get all events",
)
@alog
async def get_all_events(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[AsyncSession, Depends(get_db)]
) -> list[GetAllEventsResponse]:
    """Retrieve a list of all events.

    args:
        auth: the user's authentification status
        db: the current database

    returns:
        all events as a list
    """
    return await _get_events(db, auth.user)


@router.post(
    "/events/restSearch",
    status_code=status.HTTP_200_OK,
    summary="Search events",
)
@alog
async def rest_search_events(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[AsyncSession, Depends(get_db)],
    body: SearchEventsBody,
) -> SearchEventsResponse:
    """Search for events based on various filters.

    args:
        auth: the user's authentification status
        db: the current database
        body: the request body


    returns:
        the searched events
    """
    return await _rest_search_events(db, body, auth.user)


@router.post(
    "/events/index",
    status_code=status.HTTP_200_OK,
    summary="Search events",
)
@alog
async def index_events(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL))],
    db: Annotated[AsyncSession, Depends(get_db)],
    body: IndexEventsBody,
) -> list[IndexEventsAttributes]:
    """Search for events based on various filters, which are more general than the ones in 'rest search'.

    args:
        auth: the user's authentification status
        db: the current database
        body: the request body


    returns:
        the searched events
    """
    return await _index_events(db, body, auth.user)


@router.post(
    "/events/publish/{eventId}",
    status_code=status.HTTP_200_OK,
    summary="Publish an event",
)
@alog
async def publish_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.PUBLISH]))],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_id: Annotated[int | uuid.UUID, Path(alias="eventId")],
    request: Request,
) -> PublishEventResponse:
    """Publish an event either by its event ID or via its UUID. .

    args:
        auth: the user's authentification status
        db: the current database
        event_id: the ID or UUID of the event
        request: the request

    returns:
        the published event
    """
    return await _publish_event(db, event_id, request, auth.user)


@router.post(
    "/events/unpublish/{eventId}",
    status_code=status.HTTP_200_OK,
    summary="Unpublish an event",
)
@alog
async def unpublish_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_id: Annotated[int | uuid.UUID, Path(alias="eventId")],
    request: Request,
) -> UnpublishEventResponse:
    """Unpublish an event  either by its event ID or via its UUID.

    args:
        auth: the user's authentification status
        db: the current database
        event_id: the ID or UUID of the event
        request: the request

    returns:
        the unpublished event
    """
    return await _unpublish_event(db, event_id, request, auth.user)


@router.post(
    "/events/addTag/{eventId}/{tagId}/local:{local}",
    status_code=status.HTTP_200_OK,
    summary="Add tag to event",
)
@alog
async def add_tag_to_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.TAGGER]))],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_id: Annotated[int | uuid.UUID, Path(alias="eventId")],
    tag_id: Annotated[str, Path(alias="tagId")],
    local: str,
) -> AddRemoveTagEventsResponse:
    """Add a tag to an event by their ids.

    args:
        auth: the user's authentification status
        db: the current database
        event_id: the event ID or UUID
        tag_id: the tag ID
        local: "1" if local

    returns:
        the result of adding the tag to the event given by the api
    """
    return await _add_tag_to_event(db, event_id, tag_id, local, auth.user)


@router.post(
    "/events/removeTag/{eventId}/{tagId}",
    status_code=status.HTTP_200_OK,
    summary="Remove tag of event",
)
@alog
async def remove_tag_from_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.TAGGER]))],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_id: Annotated[uuid.UUID | int, Path(alias="eventId")],
    tag_id: Annotated[str, Path(alias="tagId")],
) -> AddRemoveTagEventsResponse:
    """Remove a tag to from an event by their IDs.

    args:
        auth: the user's authentification status
        db: the current database
        event_id: the event ID or UUID
        tag_id: the tag ID

    returns:
        the result of removing the tag from the event given by the api
    """
    return await _remove_tag_from_event(db, event_id, tag_id, auth.user)


@router.post(
    "/events/freeTextImport/{eventID}",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="start the freetext import process via worker",
)
@alog
async def start_freeTextImport(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    event_id: Annotated[int | uuid.UUID, Path(alias="eventID")],
    body: AddAttributeViaFreeTextImportEventBody,
) -> RedirectResponse:
    """Starts the freetext import process by submitting the freetext to the worker.

    args:
        auth: the user's authentification status
        event_id: the event ID or UUID
        body: the body of the freetext

    returns:
        dict
    """

    body_dict = body.model_dump()
    if body_dict["returnMetaAttributes"] is False:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="returnMetaAttributes = false is not implemented"
        )

    user = FreeTextImportWorkerUser(user_id=auth.user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no user")

    data = FreeTextImportWorkerData(data=body_dict["value"])
    worker_body = FreeTextImportWorkerBody(user=user, data=data).model_dump()

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            f"{config.WORKER_URL}/job/processFreeText",
            json=worker_body,
            headers={"Authorization": f"Bearer {config.WORKER_KEY}"},
        )

    response_data = response.json()
    job_id = response_data["job_id"]

    return RedirectResponse(f"/jobs/processFreeText/{job_id}", status_code=status.HTTP_303_SEE_OTHER)


# --- deprecated ---


@router.post(
    "/events/add",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=AddEditGetEventResponse,
    summary="Add new event (Deprecated)",
)
@alog
async def add_event_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[AsyncSession, Depends(get_db)],
    body: AddEventBody,
) -> AddEditGetEventResponse:
    """Deprecated. Add a new event with the given details.

    args:

    - the user's authentification status

    - the current database

    - the request body

    returns:

    - the new event
    """

    return await _add_event(auth, db, body)


@router.get(
    "/events/view/{eventId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    summary="Get event details (Deprecated)",
)
@alog
async def get_event_details_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL))],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_id: Annotated[int | uuid.UUID, Path(alias="eventId")],
) -> AddEditGetEventResponse:
    """Deprecated. Retrieve details of a specific attribute by its ID.

    args:

    - the user's authentification status

    - the current database

    - the event ID

    returns:

    - the event details
    """
    return await _get_event_details(db, event_id, auth.user)


@router.put(
    "/events/edit/{eventId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=AddEditGetEventResponse,
    summary="Update an event (Deprecated)",
)
@alog
async def update_event_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_id: Annotated[int | uuid.UUID, Path(alias="eventId")],
    body: EditEventBody,
) -> AddEditGetEventResponse:
    """Deprecated. Update an existing event by its ID.

    args:

    - the user's authentification status

    - the current database

    - the event id or uuid

    - the request body

    returns:

    - the updated event
    """
    return await _update_event(db, event_id, body, auth.user)


@router.delete(
    "/events/delete/{eventId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    summary="Delete an event (Deprecated)",
)
@alog
async def delete_event_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_id: Annotated[int | uuid.UUID, Path(..., alias="eventId")],
) -> DeleteEventResponse:
    """Deprecated. Delete an existing event by its ID.

    args:

    - the user's authentification status

    - the current database

    - the event id

    returns:

    - the deleted event
    """
    return await _delete_event(db, event_id, auth.user)


# --- endpoint logic ---


@alog
async def _add_event(auth: Auth, db: AsyncSession, body: AddEventBody) -> AddEditGetEventResponse:
    if not body.info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="value 'info' is required")
    if not isinstance(body.info, str):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN_BAD_REQUEST, detail="invalid 'info'")

    user = auth.user
    if user is None:
        # this should never happen, it would mean, the user disappeared between auth and processing the request
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user not available")

    if body.uuid:
        existing_event: Event | None = (
            (await db.execute(select(Event).where(Event.uuid == body.uuid))).scalars().one_or_none()
        )
        if existing_event:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event with this UUID already exists.")

    new_event = Event(
        **{
            **body.model_dump(),
            "org_id": int(body.org_id) if body.org_id is not None else auth.org_id,
            "orgc_id": int(body.orgc_id) if body.orgc_id is not None else auth.org_id,
            "date": body.date if body.date else date.today(),
            "analysis": body.analysis if body.analysis is not None else "0",
            "timestamp": body.timestamp if body.timestamp is not None else datetime.now(),
            "threat_level_id": int(body.threat_level_id) if body.threat_level_id is not None else 4,
            "user_id": user.id,
        }
    )

    await execute_blocking_workflow("event-before-save", db, new_event)
    db.add(new_event)
    await db.flush()
    await db.refresh(new_event)

    event = await _get_event(
        new_event.id,
        db,
        user,
        include_basic_event_attributes=True,
        include_non_galaxy_attribute_tags=True,
        #        populate_existing=True,
    )
    if event is None:
        raise ValueError("event is not available after adding")

    await execute_workflow("event-after-save", db, event)

    event_data = await _prepare_event_response(db, event, user)

    return AddEditGetEventResponse(Event=event_data)


@alog
async def _get_event_details(db: AsyncSession, event_id: int | uuid.UUID, user: User | None) -> AddEditGetEventResponse:
    event = await _get_event(
        event_id, db, user, include_basic_event_attributes=True, include_non_galaxy_attribute_tags=True
    )

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if not event.can_access(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    event_data = await _prepare_event_response(db, event, user)

    return AddEditGetEventResponse(Event=event_data)


@alog
async def _update_event(
    db: AsyncSession, event_id: int | uuid.UUID, body: EditEventBody, user: User | None
) -> AddEditGetEventResponse:
    event = await _get_event(
        event_id, db, user, include_basic_event_attributes=True, include_non_galaxy_attribute_tags=False
    )

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if not event.can_edit(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    event.patch(**body.model_dump(exclude_unset=True))
    event.timestamp = datetime.now()
    await execute_blocking_workflow("event-before-save", db, event)
    await db.flush()
    await db.refresh(event)
    await execute_workflow("event-after-save", db, event)

    event_data = await _prepare_event_response(db, event, user)

    return AddEditGetEventResponse(Event=event_data)


@alog
async def _delete_event(db: AsyncSession, event_id: int | uuid.UUID, user: User | None) -> DeleteEventResponse:
    event = await _get_event(
        event_id, db, user, include_basic_event_attributes=True, include_non_galaxy_attribute_tags=False
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=jsonable_encoder(
                DeleteEventResponse(
                    saved=False,
                    name="Could not delete Event",
                    message="Could not delete Event",
                    url=f"/events/delete/{event_id}",
                    id=event_id,
                ).model_dump()
            ),
        )

    if not event.can_edit(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=jsonable_encoder(
                DeleteEventResponse(
                    saved=False,
                    name="Invalid access",
                    message="Invalid permissions",
                    url=f"/events/delete/{event_id}",
                    id=event_id,
                ).model_dump()
            ),
        )

    await db.delete(event)
    await db.flush()

    return DeleteEventResponse(
        saved=True,
        success=True,
        name="Event deleted",
        message="Event deleted",
        url=f"/events/delete/{event_id}",
        id=event_id,
    )


@alog
async def _get_events(db: AsyncSession, user: User | None) -> list[GetAllEventsResponse]:
    if not user:  # Since the auth.user can be User or None
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid user")

    result = await db.execute(
        select(Event)
        .filter(Event.can_access(user))
        .options(
            selectinload(Event.org),
            selectinload(Event.orgc),
            selectinload(Event.eventtags_galaxy)
            .selectinload(EventTag.tag)
            .selectinload(Tag.galaxy_cluster)
            .options(
                selectinload(GalaxyCluster.org),
                selectinload(GalaxyCluster.orgc),
                selectinload(GalaxyCluster.galaxy),
                selectinload(GalaxyCluster.galaxy_elements),
            ),
            selectinload(Event.tags),
            selectinload(Event.eventtags).selectinload(EventTag.tag),
            selectinload(Event.creator),
            selectinload(Event.sharing_group),
        )
    )
    events: Sequence[Event] = result.scalars().all()

    # if not events:
    # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No events found.")

    event_responses = [_prepare_all_events_response(event, user) for event in events]

    return event_responses


@alog
async def _rest_search_events(db: AsyncSession, body: SearchEventsBody, user: User | None) -> SearchEventsResponse:
    if body.returnFormat != "json":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid output format.")

    qry = (
        select(Event)
        .filter(Event.can_access(user))
        .options(
            selectinload(Event.org),
            selectinload(Event.orgc),
            selectinload(Event.tags),
            selectinload(Event.eventtags_galaxy),
            selectinload(Event.eventtags),
            selectinload(Event.mispobjects),
            selectinload(Event.attributes).options(
                selectinload(Attribute.sharing_group).options(
                    selectinload(SharingGroup.sharing_group_orgs),
                    selectinload(SharingGroup.organisations),
                    selectinload(SharingGroup.creator_org),
                ),
                selectinload(Attribute.attributetags_galaxy)
                .selectinload(AttributeTag.tag)
                .selectinload(Tag.galaxy_cluster)
                .options(
                    selectinload(GalaxyCluster.org),
                    selectinload(GalaxyCluster.orgc),
                    selectinload(GalaxyCluster.galaxy),
                    selectinload(GalaxyCluster.galaxy_elements),
                ),
                selectinload(Attribute.attributetags).selectinload(AttributeTag.tag),
            ),
            with_loader_criteria(Attribute, Attribute.can_access(user)),
            selectinload(Event.sharing_group).options(
                selectinload(SharingGroup.sharing_group_orgs),
                selectinload(SharingGroup.organisations),
                selectinload(SharingGroup.creator_org),
            ),
        )
    )
    if body.limit is not None:
        page = body.page or 1
        qry = qry.limit(body.limit).offset(body.limit * (page - 1))

    result = await db.execute(qry)
    events: Sequence[Event] = result.scalars().all()

    response_list = []
    for event in events:
        response_list.append(AddEditGetEventResponse(Event=await _prepare_event_response(db, event, user)))

    return SearchEventsResponse(response=response_list)


@alog
async def _index_events(db: AsyncSession, body: IndexEventsBody, user: User | None) -> list[IndexEventsAttributes]:
    limit = 25
    offset = 0

    if body.limit:
        limit = body.limit
    if body.page:
        offset = limit * (body.page - 1)

    query: Select = (
        select(Event)
        .options(
            selectinload(Event.org),
            selectinload(Event.orgc),
            selectinload(Event.tags),
            selectinload(Event.eventtags_galaxy)
            .selectinload(EventTag.tag)
            .selectinload(Tag.galaxy_cluster)
            .options(
                selectinload(GalaxyCluster.org),
                selectinload(GalaxyCluster.orgc),
                selectinload(GalaxyCluster.galaxy),
                selectinload(GalaxyCluster.galaxy_elements),
            ),
            selectinload(Event.eventtags),
            selectinload(Event.attributes).options(
                selectinload(Attribute.attributetags_galaxy)
                .selectinload(AttributeTag.tag)
                .selectinload(Tag.galaxy_cluster)
                .options(
                    selectinload(GalaxyCluster.org),
                    selectinload(GalaxyCluster.orgc),
                    selectinload(GalaxyCluster.galaxy),
                    selectinload(GalaxyCluster.galaxy_elements),
                )
            ),
            with_loader_criteria(Attribute, Attribute.can_access(user)),
            selectinload(Event.mispobjects),
            selectinload(Event.creator),
            selectinload(Event.sharing_group),
        )
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    events: Sequence[Event] = result.scalars().all()

    response_list = [_prepare_all_events_response_index(event, user) for event in events]

    return response_list


@alog
async def _publish_event(
    db: AsyncSession, event_id: int | uuid.UUID, request: Request, user: User | None
) -> PublishEventResponse:
    event = await _get_event(
        event_id, db, user, include_basic_event_attributes=True, include_non_galaxy_attribute_tags=False
    )

    if not event:
        return PublishEventResponse(
            name="You do not have the permission to do that.",
            message="You do not have the permission to do that.",
            url=str(request.url.path),
        )

    if not event.can_edit(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    await execute_blocking_workflow("event-publish", db, event)

    await action_publish_event(db, event)

    return PublishEventResponse(
        saved=True, success=True, name="Job queued", message="Job queued", url=str(request.url.path), id=event_id
    )


@alog
async def _unpublish_event(
    db: AsyncSession, event_id: int | uuid.UUID, request: Request, user: User | None
) -> UnpublishEventResponse:
    event = await _get_event(
        event_id, db, user, include_basic_event_attributes=True, include_non_galaxy_attribute_tags=False
    )

    if not event:
        return UnpublishEventResponse(name="Invalid event.", message="Invalid event.", url=str(request.url.path))

    if not event.can_edit(user):
        return UnpublishEventResponse(name="Invalid access.", message="Invalid permissions.", url=str(request.url.path))

    setattr(event, "published", False)
    setattr(event, "publish_timestamp", 0)

    await db.flush()
    await db.refresh(event)

    return UnpublishEventResponse(
        saved=True,
        success=True,
        name="Event unpublished.",
        message="Event unpublished.",
        url=str(request.url.path),
        id=event_id,
    )


@alog
async def _add_tag_to_event(
    db: AsyncSession, event_id: int | uuid.UUID, tag_id: str, local: str, user: User | None
) -> AddRemoveTagEventsResponse:
    event = await _get_event(
        event_id, db, user, include_basic_event_attributes=True, include_non_galaxy_attribute_tags=False
    )

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    try:
        int(tag_id)
    except ValueError:
        return AddRemoveTagEventsResponse(saved=False, errors="Invalid Tag")

    tag = await db.get(Tag, tag_id)

    if not tag:
        return AddRemoveTagEventsResponse(saved=False, errors="Tag could not be added.")

    if local not in ["0", "1"]:
        local = "0"

    new_event_tag = EventTag(event_id=event.id, tag_id=tag.id, local=True if int(local) == 1 else False)

    db.add(new_event_tag)
    await db.flush()
    await db.refresh(new_event_tag)

    return AddRemoveTagEventsResponse(saved=True, success="Tag added", check_publish=True)


@alog
async def _remove_tag_from_event(
    db: AsyncSession, event_id: int | uuid.UUID, tag_id: str, user: User | None
) -> AddRemoveTagEventsResponse:
    event = await _get_event(
        event_id, db, user, include_basic_event_attributes=True, include_non_galaxy_attribute_tags=False
    )

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    try:
        int(tag_id)
    except ValueError:
        return AddRemoveTagEventsResponse(saved=False, errors="Invalid Tag")

    if not await db.get(Tag, tag_id):
        return AddRemoveTagEventsResponse(saved=False, errors="Tag could not be removed.")

    if not event.can_edit(user):
        return AddRemoveTagEventsResponse(saved=False, errors="Can not edit event.")

    result = await db.execute(select(EventTag).filter(EventTag.event_id == event.id).limit(1))

    event_tag = result.scalars().first()

    if not event_tag:
        return AddRemoveTagEventsResponse(saved=False, errors="Invalid event - tag combination.")

    await db.delete(event_tag)
    await db.flush()

    return AddRemoveTagEventsResponse(saved=True, success="Tag removed", check_publish=True)


@alog
async def _prepare_event_response(db: AsyncSession, event: Event, user: User | None) -> AddEditGetEventDetails:
    event_dict = event.asdict()

    fields_to_convert = ["sharing_group_id", "timestamp", "publish_timestamp"]
    for field in fields_to_convert:
        if event_dict.get(field) is not None:
            event_dict[field] = str(event_dict[field])
        else:
            event_dict[field] = "0"

    event_dict["date"] = str(event_dict["date"])

    org = event.org
    orgc = event.orgc

    if org is not None:
        event_dict["Org"] = AddEditGetEventOrg(id=org.id, name=org.name, uuid=org.uuid, local=org.local)
    if orgc is not None:
        event_dict["Orgc"] = AddEditGetEventOrg(id=orgc.id, name=orgc.name, uuid=orgc.uuid, local=orgc.local)

    attribute_list = event.attributes

    if event.sharing_group is not None:
        sgos = list(_compute_sgos_dict(x) for x in event.sharing_group.sharing_group_orgs)

        event_dict["SharingGroup"] = EventSharingGroupResponse(
            **event.sharing_group.asdict(),
            Organisation=event.sharing_group.creator_org.asdict(),
            SharingGroupOrg=sgos,
            SharingGroupServer=[],
        )

    if len(attribute_list) > 0:
        event_dict["Attribute"] = await _prepare_attribute_response(db, attribute_list)

    event_tag_list = event.eventtags

    if len(event_tag_list) > 0:
        event_dict["Tag"] = await _prepare_tag_response(event_tag_list)

    object_list = event.mispobjects

    if len(object_list) > 0:
        event_dict["Object"] = await _prepare_object_response(db, object_list)

    result = await db.execute(select(EventReport).filter(EventReport.event_id == event.id))
    event_report_list = result.scalars().all()

    if len(event_report_list) > 0:
        event_dict["EventReport"] = _prepare_event_report_response(event_report_list)

    galaxy_cluster_by_galaxy = defaultdict(list)

    for eventtag in event.eventtags_galaxy:
        tag = eventtag.tag
        result = await db.execute(
            select(GalaxyCluster)
            .filter(GalaxyCluster.tag_name == tag.name)
            .options(
                selectinload(GalaxyCluster.org),
                selectinload(GalaxyCluster.orgc),
                selectinload(GalaxyCluster.galaxy),
                selectinload(GalaxyCluster.galaxy_elements),
            )
        )
        galaxy_cluster = result.scalars().one_or_none()

        if galaxy_cluster is not None:
            gc_cluster = await _prepare_single_galaxy_cluster_response(galaxy_cluster, eventtag)
            galaxy_cluster_by_galaxy[galaxy_cluster.galaxy].append(gc_cluster)

    galaxy_response_list = []

    for galaxy, galaxy_cluster_responses in galaxy_cluster_by_galaxy.items():
        galaxy_dict = galaxy.asdict()
        galaxy_dict["GalaxyCluster"] = galaxy_cluster_responses

        galaxy_response_list.append(AddEditGetEventGalaxy(**galaxy_dict))

    event_dict["Galaxy"] = galaxy_response_list
    event_dict["date"] = str(event_dict["date"])

    if event.creator is not None and user is not None:
        if (
            user.role.check_permission(Permission.SITE_ADMIN)
            or event.orgc_id == user.org_id
            and user.role.check_permission(Permission.AUDIT)
        ):
            event_dict["event_creator_email"] = event.creator.email

    else:
        logger.warning("User not found with id: %s Event id: %s", event.user_id, event.id)
        logger.warning("_prepare_event_response Event: %s", event.__dict__)

    return AddEditGetEventDetails(**event_dict)


@alog
async def _prepare_attribute_response(
    db: AsyncSession, attribute_list: Sequence[Attribute]
) -> list[AddEditGetEventAttribute]:
    attribute_response_list = []

    for attribute in attribute_list:
        attribute_dict = attribute.asdict()

        if attribute.sharing_group is not None:
            sgos = list(_compute_sgos_dict(x) for x in attribute.sharing_group.sharing_group_orgs)

            attribute_dict["SharingGroup"] = EventSharingGroupResponse(
                **attribute.sharing_group.asdict(),
                Organisation=attribute.sharing_group.creator_org.asdict(),
                SharingGroupOrg=sgos,
                SharingGroupServer=[],
            )
            #            attribute_dict["SharingGroup"] = attribute.sharing_group.asdict()

        attribute_tag_list = attribute.attributetags

        if len(attribute_tag_list) > 0:
            attribute_dict["Tag"] = await _prepare_tag_response(attribute_tag_list)

        fields_to_convert = ["object_id", "sharing_group_id"]
        for field in fields_to_convert:
            if attribute_dict.get(field) is not None:
                attribute_dict[field] = str(attribute_dict[field])
            else:
                attribute_dict[field] = "0"

        attribute_dict["Galaxy"] = []

        galaxy_cluster_by_galaxy = defaultdict(list)

        for attributetag in attribute.attributetags_galaxy:
            tag = attributetag.tag
            galaxy_cluster = tag.galaxy_cluster

            if galaxy_cluster is not None:
                gc_cluster = await _prepare_single_galaxy_cluster_response(galaxy_cluster, attributetag)
                galaxy_cluster_by_galaxy[galaxy_cluster.galaxy].append(gc_cluster)

        galaxy_response_list = []

        for galaxy, galaxy_cluster_responses in galaxy_cluster_by_galaxy.items():
            galaxy_dict = galaxy.asdict()
            galaxy_dict["GalaxyCluster"] = galaxy_cluster_responses

            galaxy_response_list.append(AddEditGetEventGalaxy(**galaxy_dict))

        attribute_dict["Galaxy"] = galaxy_response_list

        attribute_response_list.append(AddEditGetEventAttribute(**attribute_dict))

    return attribute_response_list


@alog
async def _prepare_tag_response(tag_list: Sequence[EventTag | AttributeTag]) -> list[AddEditGetEventTag]:
    tag_response_list = []

    for attribute_or_event_tag in tag_list:
        tag = attribute_or_event_tag.tag
        if tag is None:
            continue

        attribute_or_event_tag_dict = tag.__dict__.copy()

        attribute_or_event_tag_dict["local"] = attribute_or_event_tag.local
        attribute_or_event_tag_dict["local_only"] = tag.local_only
        attribute_or_event_tag_dict["user_id"] = tag.user_id if tag.user_id is not None else "0"

        tag_response_list.append(AddEditGetEventTag(**attribute_or_event_tag_dict))

    return tag_response_list


@alog
async def _prepare_single_galaxy_cluster_response(
    galaxy_cluster: GalaxyCluster, connecting_tag: AttributeTag | EventTag
) -> AddEditGetEventGalaxyCluster:
    galaxy_cluster_dict = galaxy_cluster.asdict()

    if galaxy_cluster.orgc is not None:
        galaxy_cluster_dict["Orgc"] = galaxy_cluster.orgc.__dict__.copy()
    if galaxy_cluster.orgc is not None:
        galaxy_cluster_dict["Org"] = galaxy_cluster.org.__dict__.copy()
    if galaxy_cluster.galaxy_elements is not None:
        galaxy_cluster_dict["meta"] = defaultdict(list)
        for element in galaxy_cluster.galaxy_elements:
            galaxy_cluster_dict["meta"][element.key].append(element.value)

    if galaxy_cluster_dict["authors"] is not None:
        galaxy_cluster_dict["authors"] = parse_galaxy_authors(galaxy_cluster_dict["authors"])

    fields_to_convert = ["org_id", "orgc_id"]

    for field in fields_to_convert:
        if galaxy_cluster_dict.get(field) is not None:
            galaxy_cluster_dict[field] = str(galaxy_cluster_dict[field])
        else:
            galaxy_cluster_dict[field] = "0"
    galaxy_cluster_dict["collection_uuid"] = (
        galaxy_cluster.collection_uuid if galaxy_cluster.collection_uuid is not None else ""
    )

    galaxy_cluster_dict["tag_id"] = connecting_tag.tag_id

    galaxy_cluster_dict["local"] = connecting_tag.local
    galaxy_cluster_dict["relationship_type"] = connecting_tag.relationship_type or False

    if isinstance(connecting_tag, AttributeTag):
        galaxy_cluster_dict["attribute_tag_id"] = connecting_tag.id
    if isinstance(connecting_tag, EventTag):
        galaxy_cluster_dict["event_tag_id"] = connecting_tag.id

    # TODO: FIXME.
    #    result = await db.execute(
    #        select(GalaxyReference).filter(GalaxyReference.galaxy_cluster_id == galaxy_cluster.id))
    #    galaxy_cluster_relation_list = result.scalars().all()
    #
    #    if len(galaxy_cluster_relation_list) > 0:
    #        galaxy_cluster_dict["GalaxyClusterRelation"] = await _prepare_galaxy_cluster_relation_response(
    #            db, galaxy_cluster_relation_list
    #        )

    return AddEditGetEventGalaxyCluster(**galaxy_cluster_dict)


@alog
async def _prepare_galaxy_cluster_relation_response(
    db: AsyncSession, galaxy_cluster_relation_list: Sequence[GalaxyReference]
) -> list[AddEditGetEventGalaxyClusterRelation]:
    galaxy_cluster_relation_response_list = []

    for galaxy_cluster_relation in galaxy_cluster_relation_list:
        galaxy_cluster_relation_dict = galaxy_cluster_relation.__dict__.copy()

        related_galaxy_cluster = await db.get(GalaxyCluster, galaxy_cluster_relation.galaxy_cluster_id)
        if related_galaxy_cluster is None:
            continue

        result = await db.execute(select(Tag).filter(Tag.name == related_galaxy_cluster.tag_name))
        tag_list = result.scalars().all()

        if len(tag_list) > 0:
            galaxy_cluster_relation_dict["Tag"] = await _prepare_tag_response(tag_list)
            del galaxy_cluster_relation_dict["Tag"]["relationship_type"]

        galaxy_cluster_relation_response_list.append(
            AddEditGetEventGalaxyClusterRelation(**galaxy_cluster_relation_dict)
        )

    return galaxy_cluster_relation_response_list


@alog
async def _prepare_object_response(db: AsyncSession, object_list: Sequence[Object]) -> list[AddEditGetEventObject]:
    response_object_list = []

    for object in object_list:
        object_dict = object.asdict()

        result = await db.execute(
            select(Attribute)
            .options(
                selectinload(Attribute.attributetags_galaxy)
                .selectinload(AttributeTag.tag)
                .selectinload(Tag.galaxy_cluster)
                .options(
                    selectinload(GalaxyCluster.org),
                    selectinload(GalaxyCluster.orgc),
                    selectinload(GalaxyCluster.galaxy),
                    selectinload(GalaxyCluster.galaxy_elements),
                )
            )
            .filter(Attribute.object_id == object.id)
        )
        object_attribute_list = result.scalars().all()

        if len(object_attribute_list) > 0:
            object_dict["Attribute"] = await _prepare_attribute_response(db, object_attribute_list)

        response_object_list.append(AddEditGetEventObject(**object_dict))

    return response_object_list


@log
def _prepare_event_report_response(event_report_list: Sequence[EventReport]) -> AddEditGetEventEventReport:
    response_event_report_list = []

    for event_report in event_report_list:
        event_report_dict = event_report.__dict__.copy()
        response_event_report_list.append(AddEditGetEventEventReport(**event_report_dict))

    return AddEditGetEventEventReport.model_validate(response_event_report_list)


@log
def _prepare_all_events_response_index(event: Event, user: User | None) -> IndexEventsAttributes:
    event_dict = event.asdict()

    org_dict = event.org.asdict()
    orgc_dict = event.orgc.asdict()

    event_dict["Org"] = GetAllEventsOrg(**org_dict)
    event_dict["Orgc"] = GetAllEventsOrg(**orgc_dict)

    event_dict["EventTag"] = _prepare_all_events_event_tag_response(event.eventtags)

    event_dict["GalaxyCluster"] = _prepare_all_events_galaxy_cluster_response(event.eventtags_galaxy)
    event_dict["date"] = str(event_dict["date"])

    if event.sharing_group is not None:
        event_dict["SharingGroup"] = event.sharing_group.asdict()

    return IndexEventsAttributes.model_validate(event_dict)


@log
def _prepare_all_events_response(event: Event, user: User | None) -> GetAllEventsResponse:
    event_dict = event.asdict()

    org_dict = event.org.asdict()
    orgc_dict = event.orgc.asdict()

    event_dict["Org"] = GetAllEventsOrg(**org_dict)
    event_dict["Orgc"] = GetAllEventsOrg(**orgc_dict)

    event_dict["EventTag"] = _prepare_all_events_event_tag_response(event.eventtags)

    event_dict["GalaxyCluster"] = _prepare_all_events_galaxy_cluster_response(event.eventtags_galaxy)
    event_dict["date"] = str(event_dict["date"])

    if event.sharing_group is not None:
        event_dict["SharingGroup"] = event.sharing_group.asdict()

    return GetAllEventsResponse(**event_dict)


@log
def _prepare_all_events_galaxy_cluster_response(event_tag_list: Sequence[EventTag]) -> list[GetAllEventsGalaxyCluster]:
    galaxy_cluster_response_list = []

    for eventtag in event_tag_list:
        tag = eventtag.tag
        if not tag.is_galaxy:
            raise ValueError("this method should only be called with galaxy_tags!")

        galaxy_cluster = tag.galaxy_cluster
        if galaxy_cluster is None:
            # todo add some debug line
            continue
        galaxy_cluster_dict = galaxy_cluster.asdict()

        galaxy = galaxy_cluster.galaxy
        if galaxy is None or tag is None:
            continue
        galaxy_dict = galaxy.asdict().copy()
        galaxy_dict["local_only"] = tag.local_only

        galaxy_cluster_dict["tag_id"] = 0
        galaxy_cluster_dict["extends_uuid"] = ""
        galaxy_cluster_dict["collection_uuid"] = ""

        galaxy_cluster_dict["tag_id"] = tag.id
        galaxy_cluster_dict["extends_uuid"] = ""
        galaxy_cluster_dict["collection_uuid"] = ""

        galaxy_cluster_dict["Galaxy"] = GetAllEventsGalaxyClusterGalaxy(**galaxy_dict)

        galaxy_cluster_response_list.append(GetAllEventsGalaxyCluster(**galaxy_cluster_dict))

    return galaxy_cluster_response_list


@log
def _prepare_all_events_event_tag_response(event_tag_list: Sequence[EventTag]) -> list[GetAllEventsEventTag]:
    event_tag_response_list = []

    for event_tag in event_tag_list:
        event_tag_dict = event_tag.asdict()
        event_tag_dict["relationship_type"] = ""
        tag = event_tag.tag
        tag_dict = tag.asdict()
        event_tag_dict["Tag"] = GetAllEventsEventTagTag(**tag_dict)
        event_tag_response_list.append(GetAllEventsEventTag(**event_tag_dict))

    return event_tag_response_list


async def _get_event(
    event_id: int | uuid.UUID,
    db: AsyncSession,
    user: User | None,
    *,
    include_basic_event_attributes: bool = False,
    include_non_galaxy_attribute_tags: bool = False,
    populate_existing: bool = False,
) -> Event | None:
    """Get's an event by its UUID with varying amounts of included attributes loaded in.

    args:
        event_id: the UUID of the event
        db: the current db
        include_basic_event_attributes: whether to include additional load-in's
        include_basic_event_attributes: whether to also include non galaxy attribute tags

    returns:
        The event with the associated UUID or NONE in case of not being present.

    """
    query: Select = select(Event)
    if isinstance(event_id, uuid.UUID):
        query = query.filter(Event.uuid == event_id)
    else:
        query = query.filter(Event.id == event_id)

    if include_basic_event_attributes and include_non_galaxy_attribute_tags:
        query = query.options(
            selectinload(Event.org),
            selectinload(Event.orgc),
            selectinload(Event.eventtags_galaxy),
            selectinload(Event.tags),
            selectinload(Event.eventtags),
            selectinload(Event.mispobjects),
            selectinload(Event.attributes).options(
                selectinload(Attribute.sharing_group).options(
                    selectinload(SharingGroup.sharing_group_orgs),
                    selectinload(SharingGroup.organisations),
                    selectinload(SharingGroup.creator_org),
                ),
                selectinload(Attribute.attributetags_galaxy)
                .selectinload(AttributeTag.tag)
                .selectinload(Tag.galaxy_cluster)
                .options(
                    selectinload(GalaxyCluster.org),
                    selectinload(GalaxyCluster.orgc),
                    selectinload(GalaxyCluster.galaxy),
                    selectinload(GalaxyCluster.galaxy_elements),
                ),
                selectinload(Attribute.attributetags).selectinload(AttributeTag.tag),
            ),
            with_loader_criteria(Attribute, Attribute.can_access(user)),
            selectinload(Event.sharing_group).options(
                selectinload(SharingGroup.sharing_group_orgs),
                selectinload(SharingGroup.organisations),
                selectinload(SharingGroup.creator_org),
            ),
        )

    elif include_basic_event_attributes:
        query = query.options(
            selectinload(Event.org),
            selectinload(Event.orgc),
            selectinload(Event.eventtags_galaxy),
            selectinload(Event.tags),
            selectinload(Event.creator),
            selectinload(Event.eventtags),
            selectinload(Event.mispobjects),
            selectinload(Event.attributes).options(
                selectinload(Attribute.sharing_group).options(
                    selectinload(SharingGroup.sharing_group_orgs),
                    selectinload(SharingGroup.organisations),
                    selectinload(SharingGroup.creator_org),
                ),
                selectinload(Attribute.attributetags_galaxy)
                .selectinload(AttributeTag.tag)
                .selectinload(Tag.galaxy_cluster)
                .options(
                    selectinload(GalaxyCluster.org),
                    selectinload(GalaxyCluster.orgc),
                    selectinload(GalaxyCluster.galaxy),
                    selectinload(GalaxyCluster.galaxy_elements),
                ),
                selectinload(Attribute.attributetags),
            ),
            with_loader_criteria(Attribute, Attribute.can_access(user)),
            selectinload(Event.sharing_group).options(
                selectinload(SharingGroup.sharing_group_orgs),
                selectinload(SharingGroup.organisations),
                selectinload(SharingGroup.creator_org),
            ),
        )
    if populate_existing:
        query = query.execution_options(populate_existing=True)

    result = await db.execute(query)
    event = result.scalars().one_or_none()

    return event


def _compute_sgos_dict(sgo: SharingGroupOrg) -> dict:
    sgo_dict = sgo.asdict()
    sgo_dict["Organisation"] = sgo.organisation.asdict()
    return sgo_dict
