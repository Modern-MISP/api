from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
from mmisp.api_schemas.events.edit_event_body import EditEventBody
from mmisp.api_schemas.events.get_all_events_response import GetAllEventsResponse
from mmisp.api_schemas.events.index_events_body import IndexEventsBody
from mmisp.api_schemas.events.index_events_response import IndexEventsResponse
from mmisp.api_schemas.events.publish_event_response import PublishEventResponse
from mmisp.api_schemas.events.search_events_body import SearchEventsBody
from mmisp.api_schemas.events.search_events_response import SearchEventsResponse
from mmisp.api_schemas.events.unpublish_event_response import UnpublishEventResponse
from mmisp.db.database import get_db

router = APIRouter(tags=["events"])

# Sorted according to CRUD

# - Creatte a {resource}


@router.post("/events/add", deprecated=True)  # deprecated
@router.post("/events")  # new
async def events_post(body: AddEventBody, db: Session = Depends(get_db)) -> AddEditGetEventResponse:
    return AddEditGetEventResponse(Event="")


# - Read / Get a {resource}


@router.get("/events/view/{event_id}", deprecated=True)  # deprecated
@router.get("/events/{event_id}")  # new
async def events_getById(event_id: str, db: Session = Depends(get_db)) -> AddEditGetEventResponse:
    return AddEditGetEventResponse(id="")


# - Updating a {resource}


@router.put("/events/edit/{event_id}", deprecated=True)  # deprecated
@router.put("/events/{event_id}")  # new
async def events_put(event_id: str, body: EditEventBody, db: Session = Depends(get_db)) -> AddEditGetEventResponse:
    return AddEditGetEventResponse(Event="")


# - Deleting a {resource}


@router.delete("/events/delete/{event_id}", deprecated=True)  # deprecated
@router.delete("/events/{event_id}")  # new
async def events_delete(event_id: str, db: Session = Depends(get_db)) -> DeleteEventResponse:
    return DeleteEventResponse(
        saved=True,
        success=True,
        name="Event deleted.",
        message="Event deleted.",
        url=r"/events/delete/{event_id}",
        errors="Event was not deleted.",
    )


# - Get all {resource}s


@router.get("/events")
async def events_get(db: Session = Depends(get_db)) -> GetAllEventsResponse:
    return GetAllEventsResponse(events=[])


# - More niche endpoints


@router.post("/events/restSearch")
async def events_restSearch(body: SearchEventsBody, db: Session = Depends(get_db)) -> List[SearchEventsResponse]:
    return SearchEventsResponse(response=[])


@router.post("/events/index")
async def events_index(body: IndexEventsBody, db: Session = Depends(get_db)) -> List[IndexEventsResponse]:
    return IndexEventsResponse(events=[])


@router.post("/events/publish/{event_id}")
async def events_publish(event_id: str, db: Session = Depends(get_db)) -> PublishEventResponse:
    return PublishEventResponse(name="Publish", message="Job queued", url="", id="")


@router.post("/events/unpublish/{event_id}")
async def events_unpublish(event_id: str, db: Session = Depends(get_db)) -> UnpublishEventResponse:
    return UnpublishEventResponse(
        saved=True,
        success=True,
        name="Event unpublished.",
        message="Event unpublished.",
        url=r"/events/unpublish/{event_id}",
    )


@router.post("/events/addTag/{event_id}/{tag_id}/local:{local}")
async def events_addTag(
    event_id: str, tag_id: str, local: int, db: Session = Depends(get_db)
) -> AddRemoveTagEventsResponse:
    return AddRemoveTagEventsResponse(
        saved=True, success="Tag added", check_publish=True, errors="Tag could not be added."
    )


@router.post("/events/removeTag/{event_id}/{tag_id}")
async def events_removeTag(event_id: str, tag_id: str, db: Session = Depends(get_db)) -> AddRemoveTagEventsResponse:
    return AddRemoveTagEventsResponse(
        saved=True, success="Tag added", check_publish=True, errors="Tag could not be added."
    )


@router.post("/events/freeTextImport/{event_id}")
async def events_freeTextImport(
    event_id: str, body: AddAttributeViaFreeTextImportEventBody, db: Session = Depends(get_db)
) -> AddAttributeViaFreeTextImportEventResponse:
    return AddAttributeViaFreeTextImportEventResponse(comment="")
