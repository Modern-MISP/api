from typing import Annotated, List

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from starlette import status

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.events.add_attribute_via_free_text_import_event_body import (
    AddAttributeViaFreeTextImportEventBody,
)
from mmisp.api_schemas.events.add_attribute_via_free_text_import_event_response import (
    AddAttributeViaFreeTextImportEventResponse,
)
from mmisp.api_schemas.events.add_edit_get_event_response import AddEditGetEventResponse
from mmisp.api_schemas.events.add_event_body import AddEventBody
from mmisp.api_schemas.events.add_remove_tag_events_response import AddRemoveTagEventsResponse
from mmisp.api_schemas.events.delete_event_response import DeleteEventResponse
from mmisp.api_schemas.events.get_all_events_response import GetAllEventsResponse
from mmisp.api_schemas.events.index_events_body import IndexEventsBody
from mmisp.api_schemas.events.index_events_response import IndexEventsResponse
from mmisp.api_schemas.events.publish_event_response import PublishEventResponse
from mmisp.api_schemas.events.search_events_body import SearchEventsBody
from mmisp.api_schemas.events.search_events_response import SearchEventsResponse
from mmisp.api_schemas.events.unpublish_event_response import UnpublishEventResponse
from mmisp.db.database import get_db
from mmisp.util.partial import partial

router = APIRouter(tags=["events"])


# Sorted according to CRUD

# - Create a {resource}


@router.post(
    "/events",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(AddEditGetEventResponse),
    summary="Add new event",
    description="Add a new event with the given details. NOT YET AVAILABLE!",
)  # new
async def add_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    body: AddEventBody,
) -> dict:
    return await _add_event(db, body)


# - Read / Get a {resource}


@router.get(
    "/events/{eventId}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(AddEditGetEventResponse),
    summary="Get event details",
    description="Retrieve details of a specific attribute by ist ID. NOT YET AVAILABLE!",
)  # new
async def get_event_details(
    db: Annotated[Session, Depends(get_db)], event_id: Annotated[str, Path(..., alias="eventId")]
) -> dict:
    return await _get_event_details(db, event_id)


# - Updating a {resource}


@router.put(
    "/events/{eventId}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(AddEditGetEventResponse),
    summary="Update an event",
    description="Update an existing event by its ID. NOT YET AVAILABLE!",
)  # new
async def update_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
) -> dict:
    return await _update_event(db, event_id)


# - Deleting a {resource}


@router.delete(
    "/events/{eventId}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(DeleteEventResponse),
    summary="Delete an event",
    description="Delete an attribute by its ID. NOT YET AVAILABLE!",
)  # new
async def delete_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
) -> dict:
    return await _delete_event(db, event_id)


# - Get all {resource}s


@router.get(
    "/events",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(GetAllEventsResponse),
    summary="Get all attributes",
    description="Retrieve a list of all available attribute types and categories. NOT YET AVAILABLE!",
)
async def get_all_events(db: Annotated[Session, Depends(get_db)]) -> dict:
    return await _get_all_events(db)


# - More niche endpoints


@router.post(
    "/events/restSearch",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(SearchEventsResponse),
    summary="Search events",
    description="Search for events based on various filters. NOT YET AVAILABLE!",
)
async def rest_search_events(
    db: Annotated[Session, Depends(get_db)],
    body: SearchEventsBody,
) -> dict:
    return await _rest_search_events(db)


@router.post(
    "/events/index",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(IndexEventsResponse),
    summary="Search events",
    description="Search for events based on various filters, which are more general than the ones in 'rest search'."
    "NOT YET AVAILABLE!",
)
async def index_events(db: Annotated[Session, Depends(get_db)], body: IndexEventsBody) -> List[IndexEventsResponse]:
    return await _index_events(db)


@router.post(
    "/events/publish/{eventId}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(PublishEventResponse),
    summary="Publish an event",
    description="Publish an event by ist ID. NOT YET AVAILABLE!",
)
async def publish_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.PUBLISH]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
) -> dict:
    return await _publish_event(db, event_id)


@router.post(
    "/events/unpublish/{eventId}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(UnpublishEventResponse),
    summary="Unpublish an event",
    description="Unpublish an event by its ID. NOT YET AVAILABLE!",
)
async def unpublish_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
) -> dict:
    return await _unpublish_event(db, event_id)


@router.post(
    "/events/addTag/{eventId}/{tagId}/local:{local}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(AddRemoveTagEventsResponse),
    summary="Add tag to event",
    description="Add a tag to an attribute by there ids. NOT YET AVAILABLE!",
)
async def add_tag_to_event(
    local: str,
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    tag_id: Annotated[str, Path(..., alias="tagId")],
) -> dict:
    return await _add_tag_to_event(db, event_id, tag_id, local)


@router.post(
    "/events/removeTag/{eventId}/{tagId}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(AddRemoveTagEventsResponse),
    summary="Add tag to event",
    description="Add a tag to an event by there ids. NOT YET AVAILABLE!",
)
async def remove_tag_from_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    tag_id: Annotated[str, Path(..., alias="tagId")],
) -> dict:
    return await _remove_tag_from_event(db, event_id, tag_id)


@router.post(
    "/events/freeTextImport/{eventId}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(AddAttributeViaFreeTextImportEventResponse),
    summary="Add attribute to event",
    description="Add attribute to event via free text import. NOT YET AVAILABLE!",
)
async def add_attribute_via_free_text_import(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    body: AddAttributeViaFreeTextImportEventBody,
) -> dict:
    return await _add_attribute_via_free_text_import(db, event_id, body)


# - Deprecated endpoints


@router.post(
    "/events/add",
    deprecated=True,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(AddEditGetEventResponse),
    summary="Add new event (Deprecated)",
    description="Deprecated. Add a new event with the given details. NOT YET AVAILABLE!",
)
async def add_event_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    body: AddEventBody,
) -> dict:
    return await _add_event(db, body)


@router.get(
    "/events/view/{eventId}",
    deprecated=True,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(AddEditGetEventResponse),
    summary="Get event details (Deprecated)",
    description="Deprecated. Retrieve details of a specific attribute by ist ID. NOT YET AVAILABLE!",
)
async def get_event_details_depr(
    db: Annotated[Session, Depends(get_db)], event_id: Annotated[str, Path(..., alias="eventId")]
) -> dict:
    return await _get_event_details(db, event_id)


@router.put(
    "/events/edit/{eventId}",
    deprecated=True,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(AddEditGetEventResponse),
    summary="Update an event (Deprecated)",
    description="Deprecated. Update an existing event by its ID. NOT YET AVAILABLE!",
)  # new
async def update_event_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
) -> dict:
    return await _update_event(db, event_id)


@router.delete(
    "/events/delete/{eventId}",
    deprecated=True,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(AddEditGetEventResponse),
    summary="Update an event (Deprecated)",
    description="Deprecated. Update an existing event by its ID. NOT YET AVAILABLE!",
)  # new
async def delete_event_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
) -> dict:
    return _delete_event(db, event_id)


# --- endpoint logic ---


async def _add_event(db: Session, body: AddEventBody) -> dict:
    return {}


async def _get_event_details(db: Session, event_id: str) -> dict:
    return {}


async def _update_event(db: Session, event_id: str) -> dict:
    return {}


async def _delete_event(db: Session, event_id: str) -> dict:
    return DeleteEventResponse(
        saved=True,
        success=True,
        name="Event deleted.",
        message="Event deleted.",
        url=r"/events/delete/{event_id}",
        errors="Event was not deleted.",
    )


async def _get_all_events(db: Session) -> dict:
    return {}


async def _rest_search_events(db: Session) -> dict:
    return {}


async def _index_events(db: Session) -> dict:
    return {}


async def _publish_event(db: Session, event_id: str) -> dict:
    pass
    PublishEventResponse(name="Publish", message="Job queued", url="", id="")


async def _unpublish_event(db: Session, event_id: str) -> dict:
    return UnpublishEventResponse(
        saved=True,
        success=True,
        name="Event unpublished.",
        message="Event unpublished.",
        url=r"/events/unpublish/{event_id}",
    )


async def _add_tag_to_event(db: Session, event_id: str, tag_id: str, local: str) -> dict:
    return AddRemoveTagEventsResponse(
        saved=True, success="Tag added", check_publish=True, errors="Tag could not be added."
    )


async def _remove_tag_from_event(db: Session, event_id: str, tag_id: str) -> dict:
    return AddRemoveTagEventsResponse(
        saved=True, success="Tag added", check_publish=True, errors="Tag could not be added."
    )


async def _add_attribute_via_free_text_import(
    db: Session, event_id: str, body: AddAttributeViaFreeTextImportEventBody
) -> dict:
    return {}
