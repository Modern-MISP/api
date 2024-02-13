import logging
from calendar import timegm
from datetime import date
from time import gmtime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.events.add_edit_get_event_response import (
    AddEditGetEventDetails,
    AddEditGetEventOrg,
    AddEditGetEventResponse,
)
from mmisp.api_schemas.events.add_event_body import AddEventBody
from mmisp.db.database import get_db
from mmisp.db.models.event import Event
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.user import User
from mmisp.util.partial import partial

router = APIRouter(tags=["events"])
logging.basicConfig(level=logging.INFO)

info_format = "%(asctime)s - %(message)s"
error_format = "%(asctime)s - %(filename)s:%(lineno)d - %(message)s"

info_handler = logging.StreamHandler()
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter(info_format))

error_handler = logging.StreamHandler()
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(error_format))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(info_handler)
logger.addHandler(error_handler)


# Sorted according to CRUD

# - Create a {resource}


@router.post(
    "/events",
    status_code=status.HTTP_200_OK,
    response_model=partial(AddEditGetEventResponse),
    summary="Add new event",
    description="Add a new event with the given details. NOT YET AVAILABLE!",
)  # new
async def add_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    body: AddEventBody,
) -> dict:
    return await _add_event(auth, db, body)


# - Read / Get a {resource}


# @router.get(
#     "/events/{eventId}",
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(AddEditGetEventResponse),
#     summary="Get event details",
#     description="Retrieve details of a specific attribute by ist ID. NOT YET AVAILABLE!",
# )  # new
# async def get_event_details(
#     db: Annotated[Session, Depends(get_db)], event_id: Annotated[str, Path(..., alias="eventId")]
# ) -> dict:
#     return await _get_event_details(db, event_id)
#
#
# # - Updating a {resource}
#
#
# @router.put(
#     "/events/{eventId}",
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(AddEditGetEventResponse),
#     summary="Update an event",
#     description="Update an existing event by its ID. NOT YET AVAILABLE!",
# )  # new
# async def update_event(
#     auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
#     db: Annotated[Session, Depends(get_db)],
#     event_id: Annotated[str, Path(..., alias="eventId")],
# ) -> dict:
#     return await _update_event(db, event_id)
#
#
# # - Deleting a {resource}
#
#
# @router.delete(
#     "/events/{eventId}",
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(DeleteEventResponse),
#     summary="Delete an event",
#     description="Delete an attribute by its ID. NOT YET AVAILABLE!",
# )  # new
# async def delete_event(
#     auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
#     db: Annotated[Session, Depends(get_db)],
#     event_id: Annotated[str, Path(..., alias="eventId")],
# ) -> dict:
#     return await _delete_event(db, event_id)
#
#
# # - Get all {resource}s
#
#
# @router.get(
#     "/events",
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(GetAllEventsResponse),
#     summary="Get all attributes",
#     description="Retrieve a list of all available attribute types and categories. NOT YET AVAILABLE!",
# )
# async def get_all_events(db: Annotated[Session, Depends(get_db)]) -> dict:
#     return await _get_all_events(db)
#
#
# # - More niche endpoints
#
#
# @router.post(
#     "/events/restSearch",
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(SearchEventsResponse),
#     summary="Search events",
#     description="Search for events based on various filters. NOT YET AVAILABLE!",
# )
# async def rest_search_events(
#     db: Annotated[Session, Depends(get_db)],
#     body: SearchEventsBody,
# ) -> dict:
#     return await _rest_search_events(db)
#
#
# @router.post(
#     "/events/index",
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(IndexEventsResponse),
#     summary="Search events",
#     description="Search for events based on various filters, which are more general than the ones in 'rest search'."
#     "NOT YET AVAILABLE!",
# )
# async def index_events(db: Annotated[Session, Depends(get_db)], body: IndexEventsBody) -> List[IndexEventsResponse]:
#     return await _index_events(db)
#
#
# @router.post(
#     "/events/publish/{eventId}",
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(PublishEventResponse),
#     summary="Publish an event",
#     description="Publish an event by ist ID. NOT YET AVAILABLE!",
# )
# async def publish_event(
#     auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.PUBLISH]))],
#     db: Annotated[Session, Depends(get_db)],
#     event_id: Annotated[str, Path(..., alias="eventId")],
# ) -> dict:
#     return await _publish_event(db, event_id)
#
#
# @router.post(
#     "/events/unpublish/{eventId}",
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(UnpublishEventResponse),
#     summary="Unpublish an event",
#     description="Unpublish an event by its ID. NOT YET AVAILABLE!",
# )
# async def unpublish_event(
#     auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
#     db: Annotated[Session, Depends(get_db)],
#     event_id: Annotated[str, Path(..., alias="eventId")],
# ) -> dict:
#     return await _unpublish_event(db, event_id)
#
#
# @router.post(
#     "/events/addTag/{eventId}/{tagId}/local:{local}",
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(AddRemoveTagEventsResponse),
#     summary="Add tag to event",
#     description="Add a tag to an attribute by there ids. NOT YET AVAILABLE!",
# )
# async def add_tag_to_event(
#     local: str,
#     auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
#     db: Annotated[Session, Depends(get_db)],
#     event_id: Annotated[str, Path(..., alias="eventId")],
#     tag_id: Annotated[str, Path(..., alias="tagId")],
# ) -> dict:
#     return await _add_tag_to_event(db, event_id, tag_id, local)
#
#
# @router.post(
#     "/events/removeTag/{eventId}/{tagId}",
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(AddRemoveTagEventsResponse),
#     summary="Add tag to event",
#     description="Add a tag to an event by there ids. NOT YET AVAILABLE!",
# )
# async def remove_tag_from_event(
#     auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
#     db: Annotated[Session, Depends(get_db)],
#     event_id: Annotated[str, Path(..., alias="eventId")],
#     tag_id: Annotated[str, Path(..., alias="tagId")],
# ) -> dict:
#     return await _remove_tag_from_event(db, event_id, tag_id)
#
#
# @router.post(
#     "/events/freeTextImport/{eventId}",
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(AddAttributeViaFreeTextImportEventResponse),
#     summary="Add attribute to event",
#     description="Add attribute to event via free text import. NOT YET AVAILABLE!",
# )
# async def add_attribute_via_free_text_import(
#     auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
#     db: Annotated[Session, Depends(get_db)],
#     event_id: Annotated[str, Path(..., alias="eventId")],
#     body: AddAttributeViaFreeTextImportEventBody,
# ) -> dict:
#     return await _add_attribute_via_free_text_import(db, event_id, body)
#
#
# # - Deprecated endpoints
#
#
# @router.post(
#     "/events/add",
#     deprecated=True,
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(AddEditGetEventResponse),
#     summary="Add new event (Deprecated)",
#     description="Deprecated. Add a new event with the given details. NOT YET AVAILABLE!",
# )
# async def add_event_depr(
#     auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
#     db: Annotated[Session, Depends(get_db)],
#     body: AddEventBody,
# ) -> dict:
#     return await _add_event(db, body)
#
#
# @router.get(
#     "/events/view/{eventId}",
#     deprecated=True,
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(AddEditGetEventResponse),
#     summary="Get event details (Deprecated)",
#     description="Deprecated. Retrieve details of a specific attribute by ist ID. NOT YET AVAILABLE!",
# )
# async def get_event_details_depr(
#     db: Annotated[Session, Depends(get_db)], event_id: Annotated[str, Path(..., alias="eventId")]
# ) -> dict:
#     return await _get_event_details(db, event_id)
#
#
# @router.put(
#     "/events/edit/{eventId}",
#     deprecated=True,
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(AddEditGetEventResponse),
#     summary="Update an event (Deprecated)",
#     description="Deprecated. Update an existing event by its ID. NOT YET AVAILABLE!",
# )  # new
# async def update_event_depr(
#     auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
#     db: Annotated[Session, Depends(get_db)],
#     event_id: Annotated[str, Path(..., alias="eventId")],
# ) -> dict:
#     return await _update_event(db, event_id)
#
#
# @router.delete(
#     "/events/delete/{eventId}",
#     deprecated=True,
#     status_code=status.HTTP_501_NOT_IMPLEMENTED,
#     response_model=partial(AddEditGetEventResponse),
#     summary="Update an event (Deprecated)",
#     description="Deprecated. Update an existing event by its ID. NOT YET AVAILABLE!",
# )  # new
# async def delete_event_depr(
#     auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
#     db: Annotated[Session, Depends(get_db)],
#     event_id: Annotated[str, Path(..., alias="eventId")],
# ) -> dict:
#     return _delete_event(db, event_id)


# --- endpoint logic ---


async def _add_event(auth: Auth, db: Session, body: AddEventBody) -> dict:
    if not body.info:
        logger.error("Event creation failed: attribute 'info' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="value 'info' is required")

    new_event = Event(
        **{
            **body.dict(),
            "org_id": body.org_id if body.org_id is not None else auth.org_id,
            "orgc_id": body.orgc_id if body.orgc_id is not None else auth.org_id,
            "date": body.date if body.date is not None else str(date.today()),
            "analysis": body.analysis if body.analysis is not None else "0",
            "timestamp": body.timestamp if body.timestamp is not None else timegm(gmtime()),
            "threat_level_id": body.threat_level_id if body.threat_level_id is not None else 4,
            "event_creator_email": body.event_creator_email
            if body.event_creator_email is not None
            else db.query(User.email).filter(User.id == auth.user_id),
        }
    )

    try:
        db.add(new_event)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Failed to add new event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    db.refresh(new_event)
    logger.info(f"New event with id = {new_event.id} added.")

    event_data = _prepare_add_event_response(db, new_event)

    return AddEditGetEventResponse(Event=event_data)


# async def _get_event_details(db: Session, event_id: str) -> dict:
#     return {}
#
#
# async def _update_event(db: Session, event_id: str) -> dict:
#     return {}
#
#
# async def _delete_event(db: Session, event_id: str) -> dict:
#     return DeleteEventResponse(
#         saved=True,
#         success=True,
#         name="Event deleted.",
#         message="Event deleted.",
#         url=r"/events/delete/{event_id}",
#         errors="Event was not deleted.",
#     )
#
#
# async def _get_all_events(db: Session) -> dict:
#     return {}
#
#
# async def _rest_search_events(db: Session) -> dict:
#     return {}
#
#
# async def _index_events(db: Session) -> dict:
#     return {}
#
#
# async def _publish_event(db: Session, event_id: str) -> dict:
#     pass
#     PublishEventResponse(name="Publish", message="Job queued", url="", id="")
#
#
# async def _unpublish_event(db: Session, event_id: str) -> dict:
#     return UnpublishEventResponse(
#         saved=True,
#         success=True,
#         name="Event unpublished.",
#         message="Event unpublished.",
#         url=r"/events/unpublish/{event_id}",
#     )
#
#
# async def _add_tag_to_event(db: Session, event_id: str, tag_id: str, local: str) -> dict:
#     return AddRemoveTagEventsResponse(
#         saved=True, success="Tag added", check_publish=True, errors="Tag could not be added."
#     )
#
#
# async def _remove_tag_from_event(db: Session, event_id: str, tag_id: str) -> dict:
#     return AddRemoveTagEventsResponse(
#         saved=True, success="Tag added", check_publish=True, errors="Tag could not be added."
#     )
#
#
# async def _add_attribute_via_free_text_import(
#     db: Session, event_id: str, body: AddAttributeViaFreeTextImportEventBody
# ) -> dict:
#     return {}


def _prepare_add_event_response(db: Session, event: Event) -> AddEditGetEventResponse:
    event_dict = event.__dict__.copy()

    org = db.get(Organisation, event.org_id)
    orgc = db.get(Organisation, event.orgc_id)

    event_dict["Org"] = AddEditGetEventOrg(id=org.id, name=org.name, uuid=org.uuid, local=org.local)
    event_dict["Orgc"] = AddEditGetEventOrg(id=orgc.id, name=orgc.name, uuid=orgc.uuid, local=orgc.local)

    fields_to_convert = ["sharing_group_id", "timestamp", "publish_timestamp"]
    for field in fields_to_convert:
        if event_dict.get(field) is not None:
            event_dict[field] = str(event_dict[field])
        else:
            event_dict[field] = "0"

    return AddEditGetEventDetails(**event_dict)
