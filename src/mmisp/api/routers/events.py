import logging
from calendar import timegm
from datetime import date
from time import gmtime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.events.add_edit_get_event_response import (
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
)
from mmisp.api_schemas.events.add_event_body import AddEventBody
from mmisp.db.database import get_db
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.event import Event, EventReport, EventTag
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyReference
from mmisp.db.models.object import Object
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.tag import Tag
from mmisp.db.models.user import User
from mmisp.util.partial import partial
from mmisp.util.request_validations import check_existence_and_raise

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
    description="Add a new event with the given details.",
)  # new
async def add_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    body: AddEventBody,
) -> dict:
    return await _add_event(auth, db, body)


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
#     description="Add a tag to an attribute by their ids. NOT YET AVAILABLE!",
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

    user = db.get(User, auth.user_id)

    new_event = Event(
        **{
            **body.dict(),
            "org_id": int(body.org_id) if body.org_id is not None else auth.org_id,
            "orgc_id": int(body.orgc_id) if body.orgc_id is not None else auth.org_id,
            "date": body.date if body.date is not None else str(date.today()),
            "analysis": body.analysis if body.analysis is not None else "0",
            "timestamp": int(body.timestamp) if body.timestamp is not None else timegm(gmtime()),
            "threat_level_id": int(body.threat_level_id) if body.threat_level_id is not None else 4,
            "event_creator_email": body.event_creator_email if body.event_creator_email is not None else user.email,
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

    event_data = _prepare_event_response(db, new_event)

    return AddEditGetEventResponse(Event=event_data)


async def _get_event_details(db: Session, event_id: str) -> dict:
    event = check_existence_and_raise(db, Event, event_id, "event_id", "Event not found.")

    event_data = _prepare_event_response(db, event)

    return AddEditGetEventResponse(Event=event_data)


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


def _prepare_event_response(db: Session, event: Event) -> AddEditGetEventDetails:
    event_dict = event.__dict__.copy()

    fields_to_convert = ["sharing_group_id", "timestamp", "publish_timestamp"]
    for field in fields_to_convert:
        if event_dict.get(field) is not None:
            event_dict[field] = str(event_dict[field])
        else:
            event_dict[field] = "0"

    org = db.get(Organisation, event.org_id)
    orgc = db.get(Organisation, event.orgc_id)

    event_dict["Org"] = AddEditGetEventOrg(id=org.id, name=org.name, uuid=org.uuid, local=org.local)
    event_dict["Orgc"] = AddEditGetEventOrg(id=orgc.id, name=orgc.name, uuid=orgc.uuid, local=orgc.local)

    attribute_list = db.query(Attribute).filter(Attribute.event_id == event.id).all()

    event_dict["attribute_count"] = len(attribute_list)

    if len(attribute_list) > 0:
        event_dict["Attribute"] = _prepare_attribute_response(db, attribute_list)

    event_tag_list = db.query(EventTag).filter(EventTag.event_id == event.id).all()

    if len(event_tag_list) > 0:
        event_dict["Tag"] = _prepare_tag_response(db, event_tag_list, event_dict)

    object_list = db.query(Object).filter(Object.event_id == event.id).all()

    if len(object_list) > 0:
        event_dict["Object"] = _prepare_object_response(db, object_list)

    event_report_list = db.query(EventReport).filter(EventReport.event_id == event.id).all()

    if len(event_report_list) > 0:
        event_dict["EventReport"] = _prepare_event_report_response(event_report_list)

    event_dict["Galaxy"] = []

    for tag in event_tag_list:
        if tag.is_galaxy is True:
            event_dict["Galaxy"].append(
                db.get(Galaxy, db.query(GalaxyCluster).filter(GalaxyCluster.tag_name == tag.name).first().id)
            )

    event_dict["Galaxy"] = _prepare_galaxy_response(db, event_dict["Galaxy"])

    return AddEditGetEventDetails(**event_dict)


def _prepare_attribute_response(db: Session, attribute_list: list[Attribute]) -> list[AddEditGetEventAttribute]:
    attribute_response_list = []

    for attribute in attribute_list:
        attribute_dict = attribute.__dict__.copy()
        attribute_tag_list = db.query(AttributeTag).filter(AttributeTag.attribute_id == attribute.id).all()

        if len(attribute_tag_list) > 0:
            attribute_dict["Tag"] = _prepare_tag_response(db, attribute_tag_list)

        fields_to_convert = ["object_id", "sharing_group_id"]
        for field in fields_to_convert:
            if attribute_dict.get(field) is not None:
                attribute_dict[field] = str(attribute_dict[field])
            else:
                attribute_dict[field] = "0"

        attribute_response_list.append(AddEditGetEventAttribute(**attribute_dict))

    return attribute_response_list


def _prepare_tag_response(db: Session, tag_list: list[Any]) -> list[AddEditGetEventTag]:
    tag_response_list = []

    for attribute_or_event_tag in tag_list:
        tag = db.get(Tag, int(attribute_or_event_tag.tag_id))
        attribute_or_event_tag_dict = tag.__dict__.copy()

        del (
            attribute_or_event_tag_dict["attribute_count"],
            attribute_or_event_tag["count"],
            attribute_or_event_tag["favourite"],
        )

        attribute_or_event_tag_dict["local"] = attribute_or_event_tag.local
        tag_response_list.append(AddEditGetEventTag(**attribute_or_event_tag_dict))

    return tag_response_list


def _prepare_galaxy_response(db: Session, galaxy_list: list[Galaxy]) -> list[AddEditGetEventGalaxy]:
    galaxy_response_list = []

    for galaxy in galaxy_list:
        galaxy_dict = galaxy.__dict__.copy()
        galaxy_cluster_list = db.query(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id).all()

        if len(galaxy_cluster_list) > 0:
            galaxy_dict["GalaxyCluster"] = _prepare_galaxy_cluster_response(db, galaxy_cluster_list)

        galaxy_response_list.append(AddEditGetEventGalaxy(**galaxy_dict))

    return galaxy_response_list


def _prepare_galaxy_cluster_response(
    db: Session, galaxy_cluster_list: list[GalaxyCluster]
) -> list[AddEditGetEventGalaxyCluster]:
    galaxy_cluster_response_list = []

    for galaxy_cluster in galaxy_cluster_list:
        galaxy_cluster_dict = galaxy_cluster.__dict__.copy()
        galaxy_cluster_relation_list = (
            db.query(GalaxyReference).filter(GalaxyReference.galaxy_cluster_id == galaxy_cluster.id).all()
        )

        if len(galaxy_cluster_relation_list) > 0:
            galaxy_cluster_dict["GalaxyClusterRelation"] = _prepare_galaxy_cluster_relation_response(
                db, galaxy_cluster_relation_list
            )

        galaxy_cluster_response_list.append(AddEditGetEventGalaxyCluster(**galaxy_cluster_dict))

    return galaxy_cluster_response_list


def _prepare_galaxy_cluster_relation_response(
    db: Session, galaxy_cluster_relation_list: list[GalaxyReference]
) -> list[AddEditGetEventGalaxyClusterRelation]:
    galaxy_cluster_relation_response_list = []

    for galaxy_cluster_relation in galaxy_cluster_relation_list:
        galaxy_cluster_relation_dict = galaxy_cluster_relation.__dict__.copy()
        related_galaxy_cluster = (
            db.query(GalaxyCluster).filter(GalaxyCluster.id == galaxy_cluster_relation.galaxy_cluster_id).first()
        )
        tag_list = db.query(Tag).filter(Tag.name == related_galaxy_cluster.tag_name)

        if len(tag_list) > 0:
            galaxy_cluster_relation_dict["Tag"] = _prepare_tag_response(db, tag_list)
            del galaxy_cluster_relation_dict["Tag"]["relationship_type"]

        galaxy_cluster_relation_response_list.append(
            AddEditGetEventGalaxyClusterRelation(**galaxy_cluster_relation_dict)
        )

    return galaxy_cluster_relation_response_list


def _prepare_object_response(db: Session, object_list: list[Object]) -> list[AddEditGetEventObject]:
    response_object_list = []

    for object in object_list:
        object_dict = object.__dict__.copy()
        object_attribute_list = db.query(Attribute).filter(Attribute.object_id == object.id).all()

        if len(object_attribute_list) > 0:
            object_dict["Attribute"] = _prepare_attribute_response(db, object_attribute_list)

        response_object_list.append(AddEditGetEventObject(**object_dict))

    return response_object_list


def _prepare_event_report_response(event_report_list: list[EventReport]) -> AddEditGetEventEventReport:
    response_event_report_list = []

    for event_report in event_report_list:
        event_report_dict = event_report.__dict__.copy()
        response_event_report_list.append(AddEditGetEventEventReport(**event_report_dict))

    return response_event_report_list
