from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.events.delete_events_response import EventsDeleteResponse
from ..schemas.events.get_all_events_response import EventsResponse
from ..schemas.events.get_event_response import EventResponse
from ..schemas.events.search_events_body import EventsRestSearchBody
from ..schemas.events.search_events_response import EventsRestSearchResponse
from ..schemas.events.add_event_body import EventAddBody
from ..schemas.events.add_add_event_response import EventAddOrEditResponse
from ..schemas.events.index_events_body import EventsIndexBody
from ..schemas.events.index_events_response import EventsIndexResponse
from ..schemas.events.publish_event_response import EventPublishResponse
from ..schemas.events.unpublish_event_response import EventUnpublishResponse
from ..schemas.events.add_remove_tag_events_response import EventsTagResponse
from ..schemas.events.add_attribute_via_free_text_import_body import (
    EventsFreeTextImportBody,
)
from ..schemas.events.add_attribute_via_free_text_import_response import (
    EventsFreeTextImportResponse,
)
from ..schemas.events.edit_event_body import EventEditBody

router = APIRouter(prefix="/events", tags=["events"])


# -- Delete


@router.delete("/delete/{event_id}", deprecated=True)  # deprecated
@router.delete("/{event_id}")  # new
async def events_delete(
    event_id: str, db: Session = Depends(get_db)
) -> EventsDeleteResponse:
    return EventsDeleteResponse(
        saved=True,
        success=True,
        name="Event deleted.",
        message="Event deleted.",
        url="/events/delete/{\event_id}",
        errors="Event was not deleted.",
    )


# -- Get


@router.get("/")
async def events_get(db: Session = Depends(get_db)) -> EventsResponse:
    return EventsResponse(events=[])


@router.get("/view/{event_id}", deprecated=True)  # deprecated
@router.get("/{event_id}")  # new
async def events_getById(event_id: str, db: Session = Depends(get_db)) -> EventResponse:
    return EventResponse(id="")


# -- Post


@router.post("/restSearch")
async def events_restSearch(
    body: EventsRestSearchBody, db: Session = Depends(get_db)
) -> List[EventsRestSearchResponse]:
    return EventsRestSearchResponse(response=[])


@router.post("/add", deprecated=True)  # deprecated
@router.post("/")  # new
async def events_post(
    body: EventAddBody, db: Session = Depends(get_db)
) -> EventAddOrEditResponse:
    return EventAddOrEditResponse(Event="")


@router.post("/index")
async def events_index(
    body: EventsIndexBody, db: Session = Depends(get_db)
) -> List[EventsIndexResponse]:
    return EventsIndexResponse(events=[])


@router.post("/publish/{event_id}")
async def events_publish(
    event_id: str, db: Session = Depends(get_db)
) -> EventPublishResponse:
    return EventPublishResponse(name="Publish", message="Job queued", url="", id="")


@router.post("/unpublish/{event_id}")
async def events_unpublish(
    event_id: str, db: Session = Depends(get_db)
) -> EventUnpublishResponse:
    return EventUnpublishResponse(
        saved=True,
        success=True,
        name="Event unpublished.",
        message="Event unpublished.",
        url="/events/unpublish/{\event_id}",
    )


@router.post("/addTag/{event_id}/{tag_id}/local:{local}")
async def events_addTag(
    event_id: str, tag_id: str, local: int, db: Session = Depends(get_db)
) -> EventsTagResponse:
    return EventsTagResponse(
        saved=True,
        success="Tag added",
        check_publish=True,
        errors="Tag could not be added.",
    )


@router.post("/removeTag/{event_id}/{tag_id}")
async def events_removeTag(
    event_id: str, tag_id: str, db: Session = Depends(get_db)
) -> EventsTagResponse:
    return EventsTagResponse(
        saved=True,
        success="Tag added",
        check_publish=True,
        errors="Tag could not be added.",
    )


@router.post("/freeTextImport/{event_id}")
async def events_freeTextImport(
    event_id: str, body: EventsFreeTextImportBody, db: Session = Depends(get_db)
) -> EventsFreeTextImportResponse:
    return EventsFreeTextImportResponse(comment="")


# -- Put


@router.put("/edit/{event_id}", deprecated=True)  # deprecated
@router.put("/{event_id}")  # new
async def events_put(
    event_id: str, body: EventEditBody, db: Session = Depends(get_db)
) -> EventAddOrEditResponse:
    return EventAddOrEditResponse(Event="")
