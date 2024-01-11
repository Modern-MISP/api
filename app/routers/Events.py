from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.attribute import Attribute, ShadowAttribute
from ..models.event import Event, EventReport
from ..models.galaxy import Galaxy
from ..models.object import Object
from ..models.tag import Tag
from ..schemas.events.delete_events_response import EventsDeleteResponse
from ..schemas.events.get_all_events import EventsResponse
from ..schemas.events.get_event_response import EventResponse


from ..schemas.events.publish_event_response import EventPublishResponse
from ..schemas.events.unpublish_event_response import EventUnpublishResponse
from ..schemas.events.add_remove_tag_events_response import EventsTagResponse
from ..schemas.events.add_attribute_via_free_text_import_body import (
    EventsFreeTextImportBody,
)
from ..schemas.events.add_attribute_via_free_text_import_response import (
    EventsFreeTextImportResponse,
)

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


# ObjectReference[] missing
@router.post("/restSearch")
async def events_restSearch(db: Session = Depends(get_db)) -> List[Event]:
    return Attribute, Event, EventReport, Object, Tag
    # return {
    #     Events(),
    #     attributes.Attributes(),
    #     EventReport.EventReport(),
    #     objects.Objects(),
    #     tags.Tags(),
    # } - {Events.sighting_timestamp, tags.org_id, tags.inherited}


@router.post("/add")
@router.post("/")
async def events_post(db: Session = Depends(get_db)) -> Event:
    return Event
    # return {Events, organisations.local} - {Events.sighting_timestamp}


@router.post("/index")
async def events_index(db: Session = Depends(get_db)) -> List[Event]:
    return []


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
    return EventsFreeTextImportResponse


# -- Put


# ObjectReference[] missing
@router.put("/edit/{event_id}")
@router.put("/{event_id}")
async def events_put(db: Session = Depends(get_db)) -> Event:
    return ShadowAttribute, Event, Galaxy, Object, Tag
    # return {
    #     Events,
    #     galaxies.Galaxies,
    #     attributes.ShadowAttribute,
    #     object.ObjectReference,
    #     tags.Tags,
    # }
