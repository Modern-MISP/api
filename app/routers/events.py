from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.events.delete_event_response import DeleteEventResponse
from ..schemas.events.get_all_events_response import GetAllEventsResponse
from ..schemas.events.add_edit_get_event_response import AddEditGetEventResponse
from ..schemas.events.search_events_body import SearchEventsBody
from ..schemas.events.search_events_response import SearchEventsResponse
from ..schemas.events.add_event_body import AddEventBody
from ..schemas.events.index_events_body import IndexEventsBody
from ..schemas.events.index_events_response import IndexEventsResponse
from ..schemas.events.publish_event_response import PublishEventResponse
from ..schemas.events.unpublish_event_response import UnpublishEventResponse
from ..schemas.events.add_remove_tag_events_response import AddRemoveTagEventsResponse
from ..schemas.events.add_attribute_via_free_text_import_event_body import (
    AddAttributeViaFreeTextImportEventBody,
)
from ..schemas.events.add_attribute_via_free_text_import_event_response import (
    AddAttributeViaFreeTextImportEventResponse,
)
from ..schemas.events.edit_event_body import EditEventBody

router = APIRouter(prefix="/events", tags=["events"])


# -- Delete


@router.delete("/delete/{event_id}", deprecated=True)  # deprecated
@router.delete("/{event_id}")  # new
async def events_delete(
    event_id: str, db: Session = Depends(get_db)
) -> DeleteEventResponse:
    return DeleteEventResponse(
        saved=True,
        success=True,
        name="Event deleted.",
        message="Event deleted.",
        url="/events/delete/{\event_id}",
        errors="Event was not deleted.",
    )


# -- Get


@router.get("/")
async def events_get(db: Session = Depends(get_db)) -> GetAllEventsResponse:
    return GetAllEventsResponse(events=[])


@router.get("/view/{event_id}", deprecated=True)  # deprecated
@router.get("/{event_id}")  # new
async def events_getById(
    event_id: str, db: Session = Depends(get_db)
) -> AddEditGetEventResponse:
    return AddEditGetEventResponse(id="")


# -- Post


@router.post("/restSearch")
async def events_restSearch(
    body: SearchEventsBody, db: Session = Depends(get_db)
) -> List[SearchEventsResponse]:
    return SearchEventsResponse(response=[])


@router.post("/add", deprecated=True)  # deprecated
@router.post("/")  # new
async def events_post(
    body: AddEventBody, db: Session = Depends(get_db)
) -> AddEditGetEventResponse:
    return AddEditGetEventResponse(Event="")


@router.post("/index")
async def events_index(
    body: IndexEventsBody, db: Session = Depends(get_db)
) -> List[IndexEventsResponse]:
    return IndexEventsResponse(events=[])


@router.post("/publish/{event_id}")
async def events_publish(
    event_id: str, db: Session = Depends(get_db)
) -> PublishEventResponse:
    return PublishEventResponse(name="Publish", message="Job queued", url="", id="")


@router.post("/unpublish/{event_id}")
async def events_unpublish(
    event_id: str, db: Session = Depends(get_db)
) -> UnpublishEventResponse:
    return UnpublishEventResponse(
        saved=True,
        success=True,
        name="Event unpublished.",
        message="Event unpublished.",
        url="/events/unpublish/{\event_id}",
    )


@router.post("/addTag/{event_id}/{tag_id}/local:{local}")
async def events_addTag(
    event_id: str, tag_id: str, local: int, db: Session = Depends(get_db)
) -> AddRemoveTagEventsResponse:
    return AddRemoveTagEventsResponse(
        saved=True,
        success="Tag added",
        check_publish=True,
        errors="Tag could not be added.",
    )


@router.post("/removeTag/{event_id}/{tag_id}")
async def events_removeTag(
    event_id: str, tag_id: str, db: Session = Depends(get_db)
) -> AddRemoveTagEventsResponse:
    return AddRemoveTagEventsResponse(
        saved=True,
        success="Tag added",
        check_publish=True,
        errors="Tag could not be added.",
    )


@router.post("/freeTextImport/{event_id}")
async def events_freeTextImport(
    event_id: str,
    body: AddAttributeViaFreeTextImportEventBody,
    db: Session = Depends(get_db),
) -> AddAttributeViaFreeTextImportEventResponse:
    return AddAttributeViaFreeTextImportEventResponse(comment="")


# -- Put


@router.put("/edit/{event_id}", deprecated=True)  # deprecated
@router.put("/{event_id}")  # new
async def events_put(
    event_id: str, body: EditEventBody, db: Session = Depends(get_db)
) -> AddEditGetEventResponse:
    return AddEditGetEventResponse(Event="")
