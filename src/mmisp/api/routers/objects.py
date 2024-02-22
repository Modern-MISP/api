from datetime import datetime
from time import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.attributes.get_all_attributes_response import GetAllAttributesResponse
from mmisp.api_schemas.events.get_event_response import ObjectEventResponse
from mmisp.api_schemas.objects.create_object_body import ObjectCreateBody
from mmisp.api_schemas.objects.get_object_response import (
    ObjectResponse,
    ObjectSearchResponse,
    ObjectWithAttributesResponse,
)
from mmisp.api_schemas.objects.search_objects_body import ObjectSearchBody
from mmisp.api_schemas.standard_status_response import StandardStatusResponse
from mmisp.db.database import get_db, with_session_management
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.object import Object, ObjectTemplate
from mmisp.util.partial import partial

router = APIRouter(tags=["objects"])


@router.post(
    "/objects/{eventId}/{objectTemplateId}",
    status_code=status.HTTP_201_CREATED,
    response_model=partial(ObjectResponse),
    summary="Add object to event",
    description="Add a new object to a specific event using a template.",
)
@with_session_management
async def add_object(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[int, Path(alias="eventId")],
    object_template_id: Annotated[int, Path(alias="objectTemplateId")],
    body: ObjectCreateBody,
) -> dict[str, Any]:
    return await _add_object(db, event_id, object_template_id, body)


@router.post(
    "/objects/restsearch",
    status_code=status.HTTP_200_OK,
    response_model=partial(ObjectSearchResponse),
    summary="Search objects",
    description="Search for objects based on various filters.",
)
@with_session_management
async def restsearch(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: ObjectSearchBody,
) -> dict[str, Any]:
    return await _restsearch(db, body)


@router.get(
    "/objects/{objectId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(ObjectResponse),
    summary="View object details",
    description="View details of a specific object including its attributes and related event.",
)
@with_session_management
async def get_object_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[int, Path(alias="objectId")],
) -> dict[str, Any]:
    return await _get_object_details(db, object_id)


@router.delete(
    "/objects/{objectId}/{hardDelete}",
    status_code=status.HTTP_200_OK,
    response_model=partial(StandardStatusResponse),
    summary="Delete object",
    description="Delete a specific object. The hardDelete parameter determines if it's a hard or soft delete.",
)
@with_session_management
async def delete_object(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[int, Path(alias="objectId")],
    hard_delete: Annotated[bool, Path(alias="hardDelete")],
) -> dict[str, Any]:
    return await _delete_object(db, object_id, hard_delete)


# --- deprecated ---


@router.post(
    "/objects/add/{eventId}/{objectTemplateId}",
    deprecated=True,
    status_code=status.HTTP_201_CREATED,
    response_model=partial(ObjectResponse),
    summary="Add object to event (Deprecated)",
    description="Deprecated. Add an object to an event using the old route.",
)
@with_session_management
async def add_object_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[int, Path(alias="eventId")],
    object_template_id: Annotated[int, Path(alias="objectTemplateId")],
    body: ObjectCreateBody,
) -> dict[str, Any]:
    return await _add_object(db, event_id, object_template_id, body)


@router.get(
    "/objects/view/{objectId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(ObjectResponse),
    summary="View object details (Deprecated)",
    description="Deprecated. View details of a specific object using the old route.",
)
@with_session_management
async def get_object_details_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[int, Path(alias="objectId")],
) -> dict[str, Any]:
    return await _get_object_details(db, object_id)


@router.delete(
    "/objects/delete/{objectId}/{hardDelete}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(StandardStatusResponse),
    summary="Delete object (Deprecated)",
    description="""
    Deprecated. Delete a specific object using the old route.
    The hardDelete parameter determines if it's a hard or soft delete.""",
)
@with_session_management
async def delete_object_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[int, Path(alias="objectId")],
    hard_delete: Annotated[bool, Path(alias="hardDelete")],
) -> dict[str, Any]:
    return await _delete_object(db, object_id, hard_delete)


# --- endpoint logic ---


async def _add_object(db: Session, event_id: int, object_template_id: int, body: ObjectCreateBody) -> dict[str, Any]:
    template: ObjectTemplate | None = db.get(ObjectTemplate, object_template_id)

    if not template:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Object template not found.")
    if not db.get(Event, event_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found.")

    object: Object = Object(
        **body.dict(exclude={"attributes"}),
        template_id=object_template_id,
        template_name=template.name,
        template_uuid=template.uuid,
        template_version=template.version,
        template_description=template.description,
        event_id=int(event_id),
        timestamp=_create_timestamp(),
    )

    for attr in body.attributes:
        attribute: Attribute = Attribute(
            **attr.dict(exclude={"timestamp", "event_id"}),
            timestamp=_create_timestamp() if not attr.timestamp else attr.timestamp,
            event_id=int(event_id),
        )
        object.attributes.append(attribute)

    db.add(object)
    db.commit()
    db.refresh(object)
    attributes: list[Attribute] = db.query(Attribute).filter(Attribute.object_id == object.id).all()
    attributes_response: list[GetAllAttributesResponse] = [
        GetAllAttributesResponse(**attribute.asdict()) for attribute in attributes
    ]

    object_response: ObjectWithAttributesResponse = ObjectWithAttributesResponse(
        **object.__dict__,
        attributes=attributes_response,
        event=None,
    )

    return ObjectResponse(object=object_response)


async def _restsearch(db: Session, body: ObjectSearchBody) -> dict[str, Any]:
    if body.return_format is None:
        body.return_format = "json"
    else:
        _check_valid_return_format(return_format=body.return_format)

    filters = body.dict(exclude_unset=True)
    objects: list[Object] = _build_query(db=db, filters=filters)

    objects_data: list[ObjectWithAttributesResponse] = [
        ObjectWithAttributesResponse(**object.__dict__, attributes=object.attributes, event=None) for object in objects
    ]

    return ObjectSearchResponse(response=[{"object": object_data} for object_data in objects_data])


async def _get_object_details(db: Session, object_id: int) -> dict[str, Any]:
    object: Object | None = db.get(Object, object_id)

    if not object:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Object not found.")

    attributes: list[Attribute] = db.query(Attribute).filter(Attribute.object_id == object.id).all()
    event: Event = db.query(Event).join(Object, Event.id == Object.event_id).filter(Object.id == object_id).first()
    event_response: ObjectEventResponse = ObjectEventResponse(
        id=str(event.id), info=event.info, org_id=str(event.org_id), orgc_id=str(event.orgc_id)
    )

    attributes_response: list[GetAllAttributesResponse] = [
        GetAllAttributesResponse(**attribute.asdict()) for attribute in attributes
    ]
    object_data: ObjectWithAttributesResponse = ObjectWithAttributesResponse(
        **object.__dict__, attributes=attributes_response, event=event_response
    )

    return ObjectResponse(object=object_data)


async def _delete_object(db: Session, object_id: int, hard_delete: bool) -> dict[str, Any]:
    object: Object | None = db.get(Object, object_id)

    if not object:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Object not found.")

    if hard_delete:
        db.query(Attribute).filter(Attribute.object_id == object_id).delete(synchronize_session="fetch")
        db.delete(object)
        db.commit()
        saved = True
        success = True
        message = "Object has been permanently deleted."
    else:
        object.deleted = True
        db.commit()
        saved = True
        success = True
        message = "Object has been soft deleted."

    return StandardStatusResponse(
        saved=saved,
        success=success,
        name=object.name,
        message=message,
        url=f"/objects/{object_id}",
    )


def _create_timestamp() -> int:
    return int(time())


def _check_valid_return_format(return_format: str) -> None:
    if return_format not in ["json"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid return format.")


def _build_query(db: Session, filters: ObjectSearchBody) -> list[Object]:
    search_body: ObjectSearchBody = ObjectSearchBody(**filters)
    query: Object = db.query(Object)

    if search_body.object_name:
        query = query.filter(Object.name == search_body.object_name)

    if search_body.object_template_uuid:
        query = query.filter(str(Object.template_id) == search_body.object_template_uuid)

    if search_body.object_template_version:
        query = query.filter(str(Object.template_version) == search_body.object_template_version)

    if search_body.event_id:
        query = query.filter(str(Object.event_id) == search_body.event_id)

    if search_body.category:
        query = query.filter(Object.meta_category == search_body.category)

    if search_body.comment:
        query = query.filter(Object.comment.like(f"%{search_body.comment}%"))

    if search_body.first_seen:
        query = query.filter(str(Object.first_seen) == search_body.first_seen)

    if search_body.last_seen:
        query = query.filter(str(Object.last_seen) == search_body.last_seen)

    if search_body.quick_filter:
        query = query.filter(
            or_(
                Object.name.like(f"%{search_body.quick_filter}%"),
                Object.description.like(f"%{search_body.quick_filter}%"),
            )
        )

    if search_body.timestamp:
        query = query.filter(Object.timestamp == search_body.timestamp)

    if search_body.from_:
        query = query.filter(Object.timestamp >= search_body.from_)

    if search_body.to:
        query = query.filter(Object.timestamp <= search_body.to)

    if search_body.date:
        day_start = datetime.strptime(search_body.date, "%Y-%m-%d")
        start_timestamp = int(day_start.timestamp())

        day_end = day_start.replace(hour=23, minute=59, second=59)
        end_timestamp = int(day_end.timestamp())

        query = query.filter(Object.timestamp >= start_timestamp, Object.timestamp <= end_timestamp)

    if search_body.last:
        query = query.filter(Object.last_seen > search_body.last)

    if search_body.event_timestamp:
        events = db.query(Event).filter(Event.timestamp == search_body.event_timestamp).all()

        for event in events:
            query = query.filter(Object.event_id == event.id)

    if search_body.org_id:
        events = db.query(Event).filter(Event.org_id == search_body.org_id).all()

        for event in events:
            query = query.filter(Object.event_id == event.id)

    if search_body.uuid:
        query = query.filter(Object.uuid == search_body.uuid)

    if search_body.value:
        attributes = db.query(Attribute).filter(Attribute.value == search_body.value).all()

        for attribute in attributes:
            query = query.filter(Object.id == attribute.object_id)

    if search_body.value1:
        attributes = db.query(Attribute).filter(Attribute.value1 == search_body.value1).all()

        for attribute in attributes:
            query = query.filter(Object.id == attribute.object_id)

    if search_body.value2:
        attributes = db.query(Attribute).filter(Attribute.value2 == search_body.value2).all()

        for attribute in attributes:
            query = query.filter(Object.id == attribute.object_id)

    if search_body.type:
        attributes = db.query(Attribute).filter(Attribute.type == search_body.type).all()

        for attribute in attributes:
            query = query.filter(Object.id == attribute.object_id)

    if search_body.object_relation:
        query = query.filter(Object.object_relation == search_body.object_relation)

    if search_body.attribute_timestamp:
        attributes = db.query(Attribute).filter(Attribute.timestamp == search_body.attribute_timestamp).all()

        for attribute in attributes:
            query = query.filter(Object.id == attribute.object_id)

    if search_body.to_ids:
        attributes = db.query(Attribute).filter(Attribute.to_ids == search_body.to_ids).all()

        for attribute in attributes:
            query = query.filter(Object.id == attribute.object_id)

    if search_body.published:
        events = db.query(Event).filter(Event.published == search_body.published).all()

        for event in events:
            query = query.filter(Object.event_id == event.id)

    if search_body.deleted:
        query = query.filter(Object.deleted == search_body.deleted)

    if search_body.limit:
        query = query.limit(int(search_body.limit))

    return query.all()
