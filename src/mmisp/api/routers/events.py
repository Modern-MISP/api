import logging
from calendar import timegm
from collections import defaultdict
from collections.abc import Sequence
from datetime import date
from time import gmtime
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from starlette import status
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
    FreeTextProcessID,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.event import Event, EventReport, EventTag
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyReference
from mmisp.db.models.object import Object
from mmisp.db.models.tag import Tag
from mmisp.db.models.user import User
from mmisp.lib.actions import action_publish_event
from mmisp.lib.galaxies import parse_galaxy_authors
from mmisp.lib.logger import alog, log
from mmisp.util.models import update_record
from mmisp.util.partial import partial

from ..workflow import execute_blocking_workflow, execute_workflow

logger = logging.getLogger("mmisp")

router = APIRouter(tags=["events"])


@router.post(
    "/events",
    status_code=status.HTTP_200_OK,
    response_model=AddEditGetEventResponse,
    summary="Add new event",
)
@alog
async def add_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    body: AddEventBody,
) -> AddEditGetEventResponse:
    """Add a new event with the gi ven details.

    Input:

    - the user's authentification status

    - the current database

    - the request body

    Output:

    - the new event
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
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[int, Path(alias="eventId")],
) -> AddEditGetEventResponse:
    """Retrieve details of a specific event by ist ID.

    Input:

    - the user's authentification status

    - the current database

    - the id of the event

    Output:

    - the event details
    """
    return await _get_event_details(db, event_id)


@router.put(
    "/events/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=AddEditGetEventResponse,
    summary="Update an event",
)
@alog
async def update_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(alias="eventId")],
    body: EditEventBody,
) -> AddEditGetEventResponse:
    """Update an existing event by its ID.

    Input:

    - the user's authentification status

    - the current database

    - the id of the event

    - the request body

    Output:

    - the updated event
    """
    return await _update_event(db, event_id, body)


@router.delete(
    "/events/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteEventResponse,
    summary="Delete an event",
)
@alog
async def delete_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[int, Path(alias="eventId")],
) -> DeleteEventResponse:
    """Delete an attribute by its ID.

    Input:

    - the user's authentification status

    - the current database

    - the event id

    Output:

    - the deleted event
    """
    return await _delete_event(db, event_id)


@router.get(
    "/events",
    status_code=status.HTTP_200_OK,
    summary="Get all events",
)
@alog
async def get_all_events(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> list[GetAllEventsResponse]:
    """Retrieve a list of all events.

    Input:

    - the user's authentification status

    - the current database

    Output:

    - all events as a list
    """
    return await _get_events(db)


@router.post(
    "/events/restSearch",
    status_code=status.HTTP_200_OK,
    response_model=partial(SearchEventsResponse),
    summary="Search events",
)
@alog
async def rest_search_events(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: SearchEventsBody,
) -> SearchEventsResponse:
    """Search for events based on various filters.

    Input:

    - the user's authentification status

    - the current database

    - the request body

    Output:

    - the searched events
    """
    return await _rest_search_events(db, body)


@router.post(
    "/events/index",
    status_code=status.HTTP_200_OK,
    summary="Search events",
)
@alog
async def index_events(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: IndexEventsBody,
) -> list[GetAllEventsResponse]:
    """Search for events based on various filters, which are more general than the ones in 'rest search'.

    Input:

    - the user's authentification status

    - the current database

    - the request body

    Output:

    - the searched events
    """
    return await _index_events(db, body)


@router.post(
    "/events/publish/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=PublishEventResponse,
    summary="Publish an event",
)
@alog
async def publish_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.PUBLISH]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(alias="eventId")],
    request: Request,
) -> PublishEventResponse:
    """Publish an event by ist ID.

    Input:

    - the user's authentification status

    - the current database

    - the event id

    - the request

    Output:

    - the published event
    """
    return await _publish_event(db, event_id, request)


@router.post(
    "/events/unpublish/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=UnpublishEventResponse,
    summary="Unpublish an event",
)
@alog
async def unpublish_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(alias="eventId")],
    request: Request,
) -> UnpublishEventResponse:
    """Unpublish an event by its ID.

    Input:

    - the user's authentification status

    - the current database

    - the event id

    - the request

    Output:

    - the unpublished event
    """
    return await _unpublish_event(db, event_id, request)


@router.post(
    "/events/addTag/{eventId}/{tagId}/local:{local}",
    status_code=status.HTTP_200_OK,
    summary="Add tag to event",
)
@alog
async def add_tag_to_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(alias="eventId")],
    tag_id: Annotated[str, Path(alias="tagId")],
    local: str,
) -> AddRemoveTagEventsResponse:
    """Add a tag to an attribute by their ids.

    Input:

    - the user's authentification status

    - the current database

    - the event id

    - the tag id

    - local

    Output:

    - the result of adding the tag to the event given by the api
    """
    return await _add_tag_to_event(db, event_id, tag_id, local)


@router.post(
    "/events/removeTag/{eventId}/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=AddRemoveTagEventsResponse,
    summary="Remove tag of event",
)
@alog
async def remove_tag_from_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(alias="eventId")],
    tag_id: Annotated[str, Path(alias="tagId")],
) -> AddRemoveTagEventsResponse:
    """Remove a tag to from an event by their id.

    Input:

    - the user's authentification status

    - the current database

    - the event id

    - the tag id

    Output:

    - the result of removing the tag from the event given by the api
    """
    return await _remove_tag_from_event(db, event_id, tag_id)


@router.post(
    "/events/freeTextImport/{eventID}",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    response_model=FreeTextProcessID,
    summary="start the freetext import process via worker",
)
@alog
async def start_freeTextImport(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    event_id: Annotated[str, Path(alias="eventID")],
    body: AddAttributeViaFreeTextImportEventBody,
) -> FreeTextProcessID:
    """Starts the freetext import process by submitting the freetext to the worker.

    Input:

    - the user's authentification status

    - the body of the freetext

    Output:

    - dict
    """
    body_dict = body.dict()
    if body_dict["returnMetaAttributes"] is False:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="returnMetaAttributes = false is not implemented"
        )

    user = FreeTextImportWorkerUser(user_id=auth.user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no user")

    data = FreeTextImportWorkerData(data=body_dict["value"])
    worker_body = FreeTextImportWorkerBody(user=user, data=data).dict()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{config.WORKER_URL}/job/processFreeText",
            json=worker_body,
            headers={"Authorization": f"Bearer {config.WORKER_KEY}"},
        )

    response_data = response.json()
    job_id = response_data["job_id"]

    return FreeTextProcessID(id=job_id)


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
    db: Annotated[Session, Depends(get_db)],
    body: AddEventBody,
) -> AddEditGetEventResponse:
    """Deprecated. Add a new event with the given details.

    Input:

    - the user's authentification status

    - the current database

    - the request body

    Output:

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
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[int, Path(alias="eventId")],
) -> AddEditGetEventResponse:
    """Deprecated. Retrieve details of a specific attribute by its ID.

    Input:

    - the user's authentification status

    - the current database

    - the event id

    Output:

    - the event details
    """
    return await _get_event_details(db, event_id)


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
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(alias="eventId")],
    body: EditEventBody,
) -> AddEditGetEventResponse:
    """Deprecated. Update an existing event by its ID.

    Input:

    - the user's authentification status

    - the current database

    - the event id

    - the request body

    Output:

    - the updated event
    """
    return await _update_event(db, event_id, body=body)


@router.delete(
    "/events/delete/{eventId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=DeleteEventResponse,
    summary="Delete an event (Deprecated)",
)
@alog
async def delete_event_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[int, Path(..., alias="eventId")],
) -> DeleteEventResponse:
    """Deprecated. Delete an existing event by its ID.

    Input:

    - the user's authentification status

    - the current database

    - the event id

    Output:

    - the deleted event
    """
    return await _delete_event(db, event_id)


# --- endpoint logic ---


@alog
async def _add_event(auth: Auth, db: Session, body: AddEventBody) -> AddEditGetEventResponse:
    if not body.info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="value 'info' is required")
    if not isinstance(body.info, str):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN_BAD_REQUEST, detail="invalid 'info'")

    user = await db.get(User, auth.user_id)
    if user is None:
        # this should never happen, it would mean, the user disappeared between auth and processing the request
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user not available")

    new_event = Event(
        **{
            **body.dict(),
            "org_id": int(body.org_id) if body.org_id is not None else auth.org_id,
            "orgc_id": int(body.orgc_id) if body.orgc_id is not None else auth.org_id,
            "date": body.date if body.date else date.today(),
            "analysis": body.analysis if body.analysis is not None else "0",
            "timestamp": int(body.timestamp) if body.timestamp is not None else timegm(gmtime()),
            "threat_level_id": int(body.threat_level_id) if body.threat_level_id is not None else 4,
            "user_id": user.id,
        }
    )

    await execute_blocking_workflow("event-before-save", db, new_event)
    db.add(new_event)
    await db.flush()
    await db.refresh(new_event)

    result = await db.execute(
        select(Event)
        .filter(Event.id == new_event.id)
        .options(
            selectinload(Event.org),
            selectinload(Event.orgc),
            selectinload(Event.eventtags_galaxy),
            selectinload(Event.tags),
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
                ),
                selectinload(Attribute.attributetags).selectinload(AttributeTag.tag),
            ),
            selectinload(Event.mispobjects),
        )
        .execution_options(populate_existing=True)
    )
    event = result.scalars().one()

    await execute_workflow("event-after-save", db, event)

    event_data = await _prepare_event_response(db, event)

    return AddEditGetEventResponse(Event=event_data)


@alog
async def _get_event_details(db: Session, event_id: int) -> AddEditGetEventResponse:
    result = await db.execute(
        select(Event)
        .filter(Event.id == event_id)
        .options(
            selectinload(Event.org),
            selectinload(Event.orgc),
            selectinload(Event.eventtags_galaxy),
            selectinload(Event.tags),
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
                ),
                selectinload(Attribute.attributetags).selectinload(AttributeTag.tag),
            ),
            selectinload(Event.mispobjects),
        )
    )
    event = result.scalars().one_or_none()

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    event_data = await _prepare_event_response(db, event)

    return AddEditGetEventResponse(Event=event_data)


@alog
async def _update_event(db: Session, event_id: str, body: EditEventBody) -> AddEditGetEventResponse:
    result = await db.execute(
        select(Event)
        .filter(Event.id == event_id)
        .options(
            selectinload(Event.org),
            selectinload(Event.orgc),
            selectinload(Event.eventtags_galaxy),
            selectinload(Event.tags),
            selectinload(Event.eventtags),
            selectinload(Event.mispobjects),
            selectinload(Event.attributes).options(
                selectinload(Attribute.attributetags_galaxy)
                .selectinload(AttributeTag.tag)
                .selectinload(Tag.galaxy_cluster)
                .options(
                    selectinload(GalaxyCluster.org),
                    selectinload(GalaxyCluster.orgc),
                    selectinload(GalaxyCluster.galaxy),
                    selectinload(GalaxyCluster.galaxy_elements),
                ),
            ),
        )
    )
    event = result.scalars().one_or_none()

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    update_record(event, body.dict())

    await execute_blocking_workflow("event-before-save", db, event)
    await db.flush()
    await db.refresh(event)
    await execute_workflow("event-after-save", db, event)

    event_data = await _prepare_event_response(db, event)

    return AddEditGetEventResponse(Event=event_data)


@alog
async def _delete_event(db: Session, event_id: int) -> DeleteEventResponse:
    event = await db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DeleteEventResponse(
                saved=False,
                name="Could not delete Event",
                message="Could not delete Event",
                url=f"/events/delete/{event_id}",
                id=event_id,
            ).dict(),
        )

    await db.delete(event)
    await db.flush()

    return DeleteEventResponse(
        saved=True,
        success=True,
        name="Event deleted",
        message="Event deleted",
        url=f"/events/delete/{event_id}",
        id=str(event_id),
    )


@alog
async def _get_events(db: Session) -> list[GetAllEventsResponse]:
    result = await db.execute(
        select(Event).options(
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
        )
    )
    events: Sequence[Event] = result.scalars().all()

    if not events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No events found.")

    event_responses = [_prepare_all_events_response(event, "get_all") for event in events]

    return event_responses


@alog
async def _rest_search_events(db: Session, body: SearchEventsBody) -> SearchEventsResponse:
    if body.returnFormat != "json":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid output format.")

    qry = select(Event).options(
        selectinload(Event.org),
        selectinload(Event.orgc),
        selectinload(Event.tags),
        selectinload(Event.eventtags_galaxy),
        selectinload(Event.eventtags),
        selectinload(Event.mispobjects),
        selectinload(Event.attributes).options(
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
    )
    if body.limit is not None:
        page = body.page or 1
        qry = qry.limit(body.limit).offset(body.limit * (page - 1))

    result = await db.execute(qry)
    events: Sequence[Event] = result.scalars().all()

    response_list = []
    for event in events:
        response_list.append(AddEditGetEventResponse(Event=await _prepare_event_response(db, event)))

    return SearchEventsResponse(response=response_list)


@alog
async def _index_events(db: Session, body: IndexEventsBody) -> list[GetAllEventsResponse]:
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
            selectinload(Event.mispobjects),
        )
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    events: Sequence[Event] = result.scalars().all()

    response_list = [_prepare_all_events_response(event, "index") for event in events]

    return response_list


@alog
async def _publish_event(db: Session, event_id: str, request: Request) -> PublishEventResponse:
    event = await db.get(Event, event_id)

    if not event:
        return PublishEventResponse(name="Invalid event.", message="Invalid event.", url=str(request.url.path))

    await execute_blocking_workflow("event-publish", db, event)

    await action_publish_event(db, event)

    return PublishEventResponse(
        saved=True, success=True, name="Job queued", message="Job queued", url=str(request.url.path), id=str(event_id)
    )


@alog
async def _unpublish_event(db: Session, event_id: str, request: Request) -> UnpublishEventResponse:
    event = await db.get(Event, event_id)

    if not event:
        return UnpublishEventResponse(name="Invalid event.", message="Invalid event.", url=str(request.url.path))

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
        id=str(event_id),
    )


@alog
async def _add_tag_to_event(db: Session, event_id: str, tag_id: str, local: str) -> AddRemoveTagEventsResponse:
    event: Event | None = await db.get(Event, event_id)

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

    new_event_tag = EventTag(event_id=event_id, tag_id=tag.id, local=True if int(local) == 1 else False)

    db.add(new_event_tag)
    await db.flush()
    await db.refresh(new_event_tag)

    return AddRemoveTagEventsResponse(saved=True, success="Tag added", check_publish=True)


@alog
async def _remove_tag_from_event(db: Session, event_id: str, tag_id: str) -> AddRemoveTagEventsResponse:
    event: Event | None = await db.get(Event, event_id)

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    try:
        int(tag_id)
    except ValueError:
        return AddRemoveTagEventsResponse(saved=False, errors="Invalid Tag")

    if not await db.get(Tag, tag_id):
        return AddRemoveTagEventsResponse(saved=False, errors="Tag could not be removed.")

    result = await db.execute(select(EventTag).filter(EventTag.event_id == event_id).limit(1))
    event_tag = result.scalars().first()

    if not event_tag:
        return AddRemoveTagEventsResponse(saved=False, errors="Invalid event - tag combination.")

    await db.delete(event_tag)
    await db.flush()

    return AddRemoveTagEventsResponse(saved=True, success="Tag removed", check_publish=True)


@alog
async def _prepare_event_response(db: Session, event: Event) -> AddEditGetEventDetails:
    event_dict = event.__dict__.copy()

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

    # event_dict["attribute_count"] = len(attribute_list) # there is a column in the db for that

    if len(attribute_list) > 0:
        event_dict["Attribute"] = await _prepare_attribute_response(db, attribute_list)

    event_tag_list = event.eventtags

    if len(event_tag_list) > 0:
        event_dict["Tag"] = await _prepare_tag_response(db, event_tag_list)

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
            gc_cluster = await _prepare_single_galaxy_cluster_response(db, galaxy_cluster, eventtag)
            galaxy_cluster_by_galaxy[galaxy_cluster.galaxy].append(gc_cluster)

    galaxy_response_list = []

    for galaxy, galaxy_cluster_responses in galaxy_cluster_by_galaxy.items():
        galaxy_dict = galaxy.asdict()
        galaxy_dict["GalaxyCluster"] = galaxy_cluster_responses

        galaxy_response_list.append(AddEditGetEventGalaxy(**galaxy_dict))

    event_dict["Galaxy"] = galaxy_response_list
    event_dict["date"] = str(event_dict["date"])

    user = await db.get(User, event.user_id)
    if user is not None:
        event_dict["event_creator_email"] = user.email

    return AddEditGetEventDetails(**event_dict)


@alog
async def _prepare_attribute_response(
    db: Session, attribute_list: Sequence[Attribute]
) -> list[AddEditGetEventAttribute]:
    attribute_response_list = []

    for attribute in attribute_list:
        attribute_dict = attribute.asdict()

        attribute_tag_list = attribute.attributetags

        if len(attribute_tag_list) > 0:
            attribute_dict["Tag"] = await _prepare_tag_response(db, attribute_tag_list)

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
                gc_cluster = await _prepare_single_galaxy_cluster_response(db, galaxy_cluster, attributetag)
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
async def _prepare_tag_response(db: Session, tag_list: Sequence[EventTag | AttributeTag]) -> list[AddEditGetEventTag]:
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
    db: Session, galaxy_cluster: GalaxyCluster, connecting_tag: AttributeTag | EventTag
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
    db: Session, galaxy_cluster_relation_list: Sequence[GalaxyReference]
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
            galaxy_cluster_relation_dict["Tag"] = await _prepare_tag_response(db, tag_list)
            del galaxy_cluster_relation_dict["Tag"]["relationship_type"]

        galaxy_cluster_relation_response_list.append(
            AddEditGetEventGalaxyClusterRelation(**galaxy_cluster_relation_dict)
        )

    return galaxy_cluster_relation_response_list


@alog
async def _prepare_object_response(db: Session, object_list: Sequence[Object]) -> list[AddEditGetEventObject]:
    response_object_list = []

    for object in object_list:
        object_dict = object.__dict__.copy()

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

    return AddEditGetEventEventReport.parse_obj(response_event_report_list)


@log
def _prepare_all_events_response(event: Event, request_type: str) -> GetAllEventsResponse:
    event_dict = event.__dict__.copy()
    event_dict["sharing_group_id"] = "0"

    org_dict = event.org.__dict__.copy()
    orgc_dict = event.orgc.__dict__.copy()

    event_dict["Org"] = GetAllEventsOrg(**org_dict)
    event_dict["Orgc"] = GetAllEventsOrg(**orgc_dict)

    event_dict["EventTag"] = _prepare_all_events_event_tag_response(event.eventtags)

    event_dict["GalaxyCluster"] = _prepare_all_events_galaxy_cluster_response(event.eventtags_galaxy)
    event_dict["date"] = str(event_dict["date"])
    if event.user_id:
        event_dict["event_creator_email"] = event.creator.email

    response_strategy = {"get_all": GetAllEventsResponse, "index": IndexEventsAttributes}

    response_class = response_strategy.get(request_type)

    if response_class:
        return response_class(**event_dict).dict()

    raise ValueError(f"Unknown request_type: {request_type}")


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
        event_tag_dict = event_tag.__dict__.copy()
        event_tag_dict["relationship_type"] = ""
        tag = event_tag.tag
        tag_dict = tag.__dict__.copy()
        event_tag_dict["Tag"] = GetAllEventsEventTagTag(**tag_dict)
        event_tag_response_list.append(GetAllEventsEventTag(**event_tag_dict))

    return event_tag_response_list
