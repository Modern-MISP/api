from calendar import timegm
from datetime import date
from time import gmtime
from typing import Annotated, Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.attributes.get_describe_types_response import GetDescribeTypesAttributes
from mmisp.api_schemas.events.add_attribute_via_free_text_import_event_body import (
    AddAttributeViaFreeTextImportEventBody,
)
from mmisp.api_schemas.events.add_attribute_via_free_text_import_event_response import (
    AddAttributeViaFreeTextImportEventResponse,
)
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
from mmisp.api_schemas.events.add_remove_tag_events_response import AddRemoveTagEventsResponse
from mmisp.api_schemas.events.delete_event_response import DeleteEventResponse
from mmisp.api_schemas.events.edit_event_body import EditEventBody
from mmisp.api_schemas.events.FreeTextImportWorkerBody import (
    FreeTextImportWorkerBody,
    FreeTextImportWorkerData,
    FreeTextImportWorkerUser,
)
from mmisp.api_schemas.events.get_all_events_response import (
    GetAllEventsEventTag,
    GetAllEventsEventTagTag,
    GetAllEventsGalaxyCluster,
    GetAllEventsGalaxyClusterGalaxy,
    GetAllEventsOrg,
    GetAllEventsResponse,
)
from mmisp.api_schemas.events.index_events_body import IndexEventsBody
from mmisp.api_schemas.events.index_events_response import IndexEventsAttributes
from mmisp.api_schemas.events.publish_event_response import PublishEventResponse
from mmisp.api_schemas.events.search_events_body import SearchEventsBody
from mmisp.api_schemas.events.search_events_response import SearchEventsResponse
from mmisp.api_schemas.events.unpublish_event_response import UnpublishEventResponse
from mmisp.config import config
from mmisp.db.database import get_db, with_session_management
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.event import Event, EventReport, EventTag
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyReference
from mmisp.db.models.object import Object
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.tag import Tag
from mmisp.db.models.user import User
from mmisp.util.models import update_record
from mmisp.util.partial import partial

router = APIRouter(tags=["events"])


# Sorted according to CRUD

# - Create a {resource}


@router.post(
    "/events",
    status_code=status.HTTP_200_OK,
    response_model=partial(AddEditGetEventResponse),
    summary="Add new event",
    description="Add a new event with the given details.",
)  # new
@with_session_management
async def add_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    body: AddEventBody,
) -> dict:
    return await _add_event(auth, db, body)


# - Read / Get a {resource}


@router.get(
    "/events/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(AddEditGetEventResponse),
    summary="Get event details",
    description="Retrieve details of a specific attribute by ist ID.",
)  # new
@with_session_management
async def get_event_details(
    db: Annotated[Session, Depends(get_db)], event_id: Annotated[str, Path(..., alias="eventId")]
) -> dict:
    return await _get_event_details(db, event_id)


# - Updating a {resource}


@router.put(
    "/events/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(AddEditGetEventResponse),
    summary="Update an event",
    description="Update an existing event by its ID.",
)  # new
@with_session_management
async def update_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    body: EditEventBody,
) -> dict:
    return await _update_event(db, event_id, body)


# - Deleting a {resource}


@router.delete(
    "/events/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(DeleteEventResponse),
    summary="Delete an event",
    description="Delete an attribute by its ID.",
)  # new
@with_session_management
async def delete_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
) -> dict:
    return await _delete_event(db, event_id)


# - Get all {resource}s


@router.get(
    "/events",
    status_code=status.HTTP_200_OK,
    response_model=list[partial(GetAllEventsResponse)],
    summary="Get all events",
    description="Retrieve a list of all events.",
)
@with_session_management
async def get_all_events(db: Annotated[Session, Depends(get_db)]) -> dict:
    return await _get_events(db)


# - More niche endpoints


@router.post(
    "/events/restSearch",
    status_code=status.HTTP_200_OK,
    response_model=partial(SearchEventsResponse),
    summary="Search events",
    description="Search for events based on various filters.",
)
@with_session_management
async def rest_search_events(
    db: Annotated[Session, Depends(get_db)],
    body: SearchEventsBody,
) -> dict:
    return await _rest_search_events(db, body)


@router.post(
    "/events/index",
    status_code=status.HTTP_200_OK,
    response_model=list[partial(GetAllEventsResponse)],
    summary="Search events",
    description="Search for events based on various filters, which are more general than the ones in 'rest search'.",
)
@with_session_management
async def index_events(db: Annotated[Session, Depends(get_db)], body: IndexEventsBody) -> list[IndexEventsAttributes]:
    return await _index_events(db, body)


@router.post(
    "/events/publish/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(PublishEventResponse),
    summary="Publish an event",
    description="Publish an event by ist ID.",
)
@with_session_management
async def publish_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.PUBLISH]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    request: Request,
) -> dict:
    return await _publish_event(db, event_id, request)


@router.post(
    "/events/unpublish/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(UnpublishEventResponse),
    summary="Unpublish an event",
    description="Unpublish an event by its ID.",
)
@with_session_management
async def unpublish_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    request: Request,
) -> dict:
    return await _unpublish_event(db, event_id, request)


@router.post(
    "/events/addTag/{eventId}/{tagId}/local:{local}",
    status_code=status.HTTP_200_OK,
    response_model=partial(AddRemoveTagEventsResponse),
    summary="Add tag to event",
    description="Add a tag to an attribute by their ids.",
)
@with_session_management
async def add_tag_to_event(
    local: str,
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    tag_id: Annotated[str, Path(..., alias="tagId")],
) -> dict:
    return await _add_tag_to_event(db, event_id, tag_id, local)


@router.post(
    "/events/removeTag/{eventId}/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(AddRemoveTagEventsResponse),
    summary="Add tag to event",
    description="Add a tag to an event by their ids.",
)
@with_session_management
async def remove_tag_from_event(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    tag_id: Annotated[str, Path(..., alias="tagId")],
) -> dict:
    return await _remove_tag_from_event(db, event_id, tag_id)


@router.post(
    "/events/freeTextImport/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=list[partial(AddAttributeViaFreeTextImportEventResponse)],
    summary="Add attribute to event",
    description="Add attribute to event via free text import.",
)
@with_session_management
async def add_attribute_via_free_text_import(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    body: AddAttributeViaFreeTextImportEventBody,
) -> dict:
    body_dict = body.dict()
    user = FreeTextImportWorkerUser(user_id=auth.user_id)
    data = FreeTextImportWorkerData(data=body_dict["Attribute"]["value"])
    worker_body = FreeTextImportWorkerBody(user=user, data=data).dict()
    print(worker_body)
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{config.WORKER_URL}/job/processFreeText", json=worker_body)
    response_json = response.json()
    print(response_json)
    return await _add_attribute_via_free_text_import(db, event_id, response_json)


# - Deprecated endpoints


@router.post(
    "/events/add",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(AddEditGetEventResponse),
    summary="Add new event (Deprecated)",
    description="Deprecated. Add a new event with the given details.",
)
@with_session_management
async def add_event_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    body: AddEventBody,
) -> dict:
    return await _add_event(db, body)


@router.get(
    "/events/view/{eventId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(AddEditGetEventResponse),
    summary="Get event details (Deprecated)",
    description="Deprecated. Retrieve details of a specific attribute by ist ID. NOT YET AVAILABLE!",
)
@with_session_management
async def get_event_details_depr(
    db: Annotated[Session, Depends(get_db)], event_id: Annotated[str, Path(..., alias="eventId")]
) -> dict:
    return await _get_event_details(db, event_id)


@router.put(
    "/events/edit/{eventId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(AddEditGetEventResponse),
    summary="Update an event (Deprecated)",
    description="Deprecated. Update an existing event by its ID. NOT YET AVAILABLE!",
)  # new
@with_session_management
async def update_event_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
) -> dict:
    return await _update_event(db, event_id)


@router.delete(
    "/events/delete/{eventId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(AddEditGetEventResponse),
    summary="Delete an event (Deprecated)",
    description="Deprecated. Delete an existing event by its ID. NOT YET AVAILABLE!",
)  # new
@with_session_management
async def delete_event_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
) -> dict:
    return _delete_event(db, event_id)


# --- endpoint logic ---


async def _add_event(auth: Auth, db: Session, body: AddEventBody) -> dict:
    if not body.info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="value 'info' is required")
    if not isinstance(body.info, str):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN_BAD_REQUEST, detail="invalid 'info'")

    user = db.get(User, auth.user_id)

    new_event = Event(
        **{
            **body.dict(),
            "org_id": int(body.org_id) if body.org_id is not None else auth.org_id,
            "orgc_id": int(body.orgc_id) if body.orgc_id is not None else auth.org_id,
            "date": body.date if body.date is not None else date.today(),
            "analysis": body.analysis if body.analysis is not None else "0",
            "timestamp": int(body.timestamp) if body.timestamp is not None else timegm(gmtime()),
            "threat_level_id": int(body.threat_level_id) if body.threat_level_id is not None else 4,
            "event_creator_email": body.event_creator_email if body.event_creator_email is not None else user.email,
        }
    )

    db.add(new_event)
    db.commit()

    db.refresh(new_event)

    event_data = _prepare_event_response(db, new_event)

    return AddEditGetEventResponse(Event=event_data)


async def _get_event_details(db: Session, event_id: str) -> dict:
    event: Event | None = db.get(Event, event_id)

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    event_data = _prepare_event_response(db, event)

    return AddEditGetEventResponse(Event=event_data)


async def _update_event(db: Session, event_id: str, body: EditEventBody) -> dict:
    event: Event | None = db.get(Event, event_id)

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    update_record(event, body.dict())

    db.commit()
    db.refresh(event)

    event_data = _prepare_event_response(db, event)

    return AddEditGetEventResponse(Event=event_data)


async def _delete_event(db: Session, event_id: str) -> DeleteEventResponse:
    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DeleteEventResponse(
                saved=False,
                name="Could not delete Event",
                message="Could not delete Event",
                url=f"/events/delete/{event_id}",
                errors="Event was not deleted.",
            ).dict(),
        )

    db.delete(event)
    db.commit()

    return DeleteEventResponse(
        saved=True,
        success=True,
        name="Event deleted",
        message="Event deleted",
        url=f"/events/delete/{event_id}",
        errors="Event was not deleted.",
    )


async def _get_events(db: Session) -> dict:
    events = db.query(Event).all()

    if not events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No events found.")

    event_responses = [_prepare_all_events_response(db, event) for event in events]

    return event_responses


async def _rest_search_events(db: Session, body: SearchEventsBody) -> dict:
    if body.returnFormat != "json":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid output format.")
    events = db.query(Event).all()
    for field, value in body.dict().items():
        event_dict = db.query(Event).__dict__.copy()
        if field not in event_dict:
            continue
        events = db.query(Event).filter(getattr(Event, field) == value).all()

        # todo: not all fields in 'SearchAttributesBody' are taken into account yet

    response_list = []
    for event in events:
        response_list.append(AddEditGetEventResponse(Event=_prepare_event_response(db, event)))

    return SearchEventsResponse(response=response_list)


async def _index_events(db: Session, body: IndexEventsBody) -> dict:
    events = db.query(Event).all()
    for field, value in body.dict().items():
        event_dict = db.query(Event).__dict__.copy()
        if field not in event_dict:
            continue
        events = db.query(Event).filter(getattr(Event, field) == value).all()

        # todo: not all fields in 'IndexEventsBody' are taken into account yet

    response_list = [_prepare_all_events_response(db, event) for event in events]

    return response_list


async def _publish_event(db: Session, event_id: str, request: Request) -> PublishEventResponse:
    event = db.get(Event, event_id)
    if not event:
        return PublishEventResponse(name="Invalid event.", message="Invalid event.", url=str(request.url.path))
    timegm(gmtime())

    setattr(event, "published", True)
    setattr(event, "publish_timestamp", timegm(gmtime()))

    db.commit()

    db.refresh(event)

    return PublishEventResponse(
        saved=True, success=True, name="Job queued", message="Job queued", url=str(request.url.path), id=str(event_id)
    )


async def _unpublish_event(db: Session, event_id: str, request: Request) -> UnpublishEventResponse:
    event = db.get(Event, event_id)
    if not event:
        return UnpublishEventResponse(name="Invalid event.", message="Invalid event.", url=str(request.url.path))
    timegm(gmtime())

    setattr(event, "published", False)
    setattr(event, "publish_timestamp", 0)

    db.commit()

    db.refresh(event)

    return UnpublishEventResponse(
        saved=True,
        success=True,
        name="Event unpublished.",
        message="Event unpublished.",
        url=str(request.url.path),
        id=str(event_id),
    )


async def _add_tag_to_event(db: Session, event_id: str, tag_id: str, local: str) -> dict:
    event: Event | None = db.get(Event, event_id)

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    try:
        int(tag_id)
    except ValueError:
        return AddRemoveTagEventsResponse(saved=False, errors="Invalid Tag")
    if not db.get(Tag, tag_id):
        return AddRemoveTagEventsResponse(saved=False, errors="Tag could not be added.")

    tag = db.get(Tag, tag_id)

    if local not in ["0", "1"]:
        local = 0

    new_event_tag = EventTag(event_id=event_id, tag_id=tag.id, local=True if int(local) == 1 else False)

    db.add(new_event_tag)
    db.commit()

    db.refresh(new_event_tag)

    return AddRemoveTagEventsResponse(saved=True, success="Tag added", check_publish=True)


async def _remove_tag_from_event(db: Session, event_id: str, tag_id: str) -> dict:
    event: Event | None = db.get(Event, event_id)

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    try:
        int(tag_id)
    except ValueError:
        return AddRemoveTagEventsResponse(saved=False, errors="Invalid Tag")
    if not db.get(Tag, tag_id):
        return AddRemoveTagEventsResponse(saved=False, errors="Tag could not be removed.")

    event_tag = db.query(EventTag).filter(EventTag.event_id == event_id).first()

    if not event_tag:
        return AddRemoveTagEventsResponse(saved=False, errors="Invalid event - tag combination.")

    db.delete(event_tag)
    db.commit()

    return AddRemoveTagEventsResponse(saved=True, success="Tag removed", check_publish=True)


async def _add_attribute_via_free_text_import(db: Session, event_id: str, response_json: Any) -> dict:
    event: Event | None = db.get(Event, event_id)

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    response_list = []

    for attribute in response_json["attributes"]:
        value = attribute["Items"]["value"]
        attribute_type = attribute["Items"]["default_type"]
        category = GetDescribeTypesAttributes().sane_defaults[attribute_type]["default_category"].value

        new_attribute = Attribute(event_id=event_id, value=value, type=attribute_type, category=category)

        db.add(new_attribute)
        db.commit()

        attribute_response_dict = new_attribute.__dict__.copy()
        attribute_response_dict["original_value"] = new_attribute.value
        response_list.append(AddAttributeViaFreeTextImportEventResponse(**attribute_response_dict))

    return response_list


def _prepare_event_response(db: Session, event: Event) -> AddEditGetEventDetails:
    event_dict = event.__dict__.copy()

    fields_to_convert = ["sharing_group_id", "timestamp", "publish_timestamp"]
    for field in fields_to_convert:
        if event_dict.get(field) is not None:
            event_dict[field] = str(event_dict[field])
        else:
            event_dict[field] = "0"

    event_dict["date"] = str(event_dict["date"])

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
        event_dict["Tag"] = _prepare_tag_response(db, event_tag_list)

    object_list = db.query(Object).filter(Object.event_id == event.id).all()

    if len(object_list) > 0:
        event_dict["Object"] = _prepare_object_response(db, object_list)

    event_report_list = db.query(EventReport).filter(EventReport.event_id == event.id).all()

    if len(event_report_list) > 0:
        event_dict["EventReport"] = _prepare_event_report_response(event_report_list)

    event_dict["Galaxy"] = []

    for event_tag in event_tag_list:
        tag = db.get(Tag, event_tag.tag_id)
        if tag.is_galaxy is True:
            event_dict["Galaxy"].append(
                db.get(Galaxy, db.query(GalaxyCluster).filter(GalaxyCluster.tag_name == tag.name).first().galaxy_id)
            )

    event_dict["Galaxy"] = _prepare_galaxy_response(db, event_dict["Galaxy"], event)
    event_dict["date"] = str(event_dict["date"])

    return AddEditGetEventDetails(**event_dict)


def _prepare_attribute_response(db: Session, attribute_list: list[Attribute]) -> list[AddEditGetEventAttribute]:
    attribute_response_list = []
    attribute_tag_list = []

    for attribute in attribute_list:
        attribute_dict = attribute.asdict().copy()
        attribute_tag_list = db.query(AttributeTag).filter(AttributeTag.attribute_id == attribute.id).all()

        if len(attribute_tag_list) > 0:
            attribute_dict["Tag"] = _prepare_tag_response(db, attribute_tag_list)

        fields_to_convert = ["object_id", "sharing_group_id"]
        for field in fields_to_convert:
            if attribute_dict.get(field) is not None:
                attribute_dict[field] = str(attribute_dict[field])
            else:
                attribute_dict[field] = "0"

        attribute_dict["Galaxy"] = []

        for attribute_tag in attribute_tag_list:
            tag = db.get(Tag, attribute_tag.tag_id)
            if tag.is_galaxy is True:
                attribute_dict["Galaxy"].append(
                    db.get(Galaxy, db.query(GalaxyCluster).filter(GalaxyCluster.tag_name == tag.name).first().galaxy_id)
                )

        attribute_dict["Galaxy"] = _prepare_galaxy_response(db, attribute_dict["Galaxy"], attribute)

        attribute_response_list.append(AddEditGetEventAttribute(**attribute_dict))

    return attribute_response_list


def _prepare_tag_response(db: Session, tag_list: list[Any]) -> list[AddEditGetEventTag]:
    tag_response_list = []

    for attribute_or_event_tag in tag_list:
        tag = db.get(Tag, int(attribute_or_event_tag.tag_id))
        attribute_or_event_tag_dict = tag.__dict__.copy()

        attribute_or_event_tag_dict["local"] = attribute_or_event_tag.local
        attribute_or_event_tag_dict["local_only"] = tag.inherited
        attribute_or_event_tag_dict["user_id"] = tag.user_id if tag.user_id is not None else "0"
        tag_response_list.append(AddEditGetEventTag(**attribute_or_event_tag_dict))

    return tag_response_list


def _prepare_galaxy_response(
    db: Session, galaxy_list: list[Galaxy], attribute: Attribute
) -> list[AddEditGetEventGalaxy]:
    galaxy_response_list = []

    for galaxy in galaxy_list:
        galaxy_dict = galaxy.__dict__.copy()
        galaxy_cluster_list = db.query(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id).all()

        if len(galaxy_cluster_list) > 0:
            galaxy_dict["GalaxyCluster"] = _prepare_galaxy_cluster_response(db, galaxy_cluster_list, attribute)

        galaxy_dict["local_only"] = db.query(Tag).filter(Tag.name == galaxy_cluster_list[0].tag_name).first().inherited

        galaxy_response_list.append(AddEditGetEventGalaxy(**galaxy_dict))

    return galaxy_response_list


def _prepare_galaxy_cluster_response(
    db: Session, galaxy_cluster_list: list[GalaxyCluster], data_object: Any
) -> list[AddEditGetEventGalaxyCluster]:
    galaxy_cluster_response_list = []

    for galaxy_cluster in galaxy_cluster_list:
        galaxy_cluster_dict = galaxy_cluster.__dict__.copy()
        galaxy_cluster_dict["authors"] = galaxy_cluster.authors.split(" ")
        tag = db.query(Tag).filter(Tag.name == galaxy_cluster.tag_name).first()
        fields_to_convert = ["org_id", "orgc_id", "extends_version"]
        for field in fields_to_convert:
            if galaxy_cluster_dict.get(field) is not None:
                galaxy_cluster_dict[field] = str(galaxy_cluster_dict[field])
            else:
                galaxy_cluster_dict[field] = "0"

        galaxy_cluster_dict["tag_id"] = tag.id
        galaxy_cluster_dict["extends_uuid"] = (
            galaxy_cluster.extends_uuid if galaxy_cluster.extends_uuid is not None else ""
        )
        galaxy_cluster_dict["collection_uuid"] = (
            galaxy_cluster.collection_uuid if galaxy_cluster.collection_uuid is not None else ""
        )

        if isinstance(data_object, Attribute):
            galaxy_cluster_dict["attribute_tag_id"] = (
                db.query(AttributeTag)
                .filter(AttributeTag.tag_id == tag.id)
                .filter(AttributeTag.attribute_id == data_object.id)
                .first()
                .id
            )
        elif isinstance(data_object, Event):
            galaxy_cluster_dict["event_tag_id"] = (
                db.query(EventTag)
                .filter(EventTag.tag_id == tag.id)
                .filter(EventTag.event_id == data_object.id)
                .first()
                .id
            )

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


def _prepare_all_events_response(db: Session, event: Event) -> GetAllEventsResponse:
    event_dict = event.__dict__.copy()
    event_dict["sharing_group_id"] = "0"

    org = db.get(Organisation, event.org_id)
    org_dict = org.__dict__.copy()

    orgc = db.get(Organisation, event.orgc_id)
    orgc_dict = orgc.__dict__.copy()

    event_dict["Org"] = GetAllEventsOrg(**org_dict)
    event_dict["Orgc"] = GetAllEventsOrg(**orgc_dict)

    event_tag_list = db.query(EventTag).filter(EventTag.event_id == event.id).all()
    event_dict["EventTag"] = _prepare_all_events_event_tag_response(db, event_tag_list)

    event_dict["GalaxyCluster"] = _prepare_all_events_galaxy_cluster_response(db, event_tag_list)
    event_dict["date"] = str(event_dict["date"])

    return GetAllEventsResponse(**event_dict)


def _prepare_all_events_galaxy_cluster_response(
    db: Session, event_tag_list: list[EventTag]
) -> list[GetAllEventsGalaxyCluster]:
    galaxy_cluster_response_list = []

    for event_tag in event_tag_list:
        tag = db.get(Tag, event_tag.tag_id)

        if tag.is_galaxy is True:
            galaxy_cluster_list = db.query(GalaxyCluster).filter(GalaxyCluster.tag_name == tag.name).all()

            for galaxy_cluster in galaxy_cluster_list:
                galaxy_cluster_dict = galaxy_cluster.__dict__.copy()

                galaxy = db.get(Galaxy, galaxy_cluster.galaxy_id)
                galaxy_dict = galaxy.__dict__.copy()
                galaxy_dict["local_only"] = tag.inherited

                galaxy_cluster_dict["authors"] = galaxy_cluster.authors.split(" ")
                tag = db.query(Tag).filter(Tag.name == galaxy_cluster.tag_name).first()
                galaxy_cluster_dict["org_id"] = tag.org_id if tag.org_id is not None else "0"
                galaxy_cluster_dict["orgc_id"] = tag.org_id if tag.org_id is not None else "0"
                galaxy_cluster_dict["tag_id"] = tag.id
                galaxy_cluster_dict["extends_uuid"] = ""
                galaxy_cluster_dict["extends_version"] = "0"
                galaxy_cluster_dict["collection_uuid"] = ""

                galaxy_cluster_dict["Galaxy"] = GetAllEventsGalaxyClusterGalaxy(**galaxy_dict)

                galaxy_cluster_response_list.append(GetAllEventsGalaxyCluster(**galaxy_cluster_dict))

    return galaxy_cluster_response_list


def _prepare_all_events_event_tag_response(db: Session, event_tag_list: list[EventTag]) -> list[GetAllEventsEventTag]:
    event_tag_response_list = []

    for event_tag in event_tag_list:
        event_tag_dict = event_tag.__dict__.copy()
        event_tag_dict["relationship_type"] = ""
        tag = db.get(Tag, event_tag.tag_id)
        tag_dict = tag.__dict__.copy()
        event_tag_dict["Tag"] = GetAllEventsEventTagTag(**tag_dict)
        event_tag_response_list.append(GetAllEventsEventTag(**event_tag_dict))

    return event_tag_response_list
