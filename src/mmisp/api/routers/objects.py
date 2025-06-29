from collections.abc import Sequence
from datetime import datetime
from time import time
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import delete, or_, select
from sqlalchemy.sql.expression import Select

from mmisp.api.auth import Auth, AuthStrategy, authorize
from mmisp.api_schemas.attributes import GetAllAttributesResponse
from mmisp.api_schemas.events import ObjectEventResponse
from mmisp.api_schemas.objects import (
    ObjectCreateBody,
    ObjectResponse,
    ObjectSearchBody,
    ObjectSearchResponse,
    ObjectWithAttributesResponse,
)
from mmisp.api_schemas.responses.standard_status_response import StandardStatusResponse
from mmisp.db.database import Session, get_db
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.object import Object, ObjectTemplate
from mmisp.lib.logger import alog, log

router = APIRouter(tags=["objects"])


@router.post(
    "/objects/{eventId}/{objectTemplateId}",
    status_code=status.HTTP_201_CREATED,
    response_model=ObjectResponse,
    summary="Add object to event",
)
@alog
async def add_object(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[int, Path(alias="eventId")],
    object_template_id: Annotated[int, Path(alias="objectTemplateId")],
    body: ObjectCreateBody,
) -> ObjectResponse:
    """Add a new object to a specific event using a template.

    args:

    - the user's authentification status

    - the current database

    - the event id

    - the object template id

    - the request body

    returns:

    - the added object
    """
    return await _add_object(db, event_id, object_template_id, body)


@router.post(
    "/objects/restsearch",
    status_code=status.HTTP_200_OK,
    summary="Search objects",
)
@alog
async def restsearch(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: ObjectSearchBody,
) -> ObjectSearchResponse:
    """Search for objects based on various filters.

    args:

    - the user's authentification status

    - the current database

    - the request body

    returns:

    - the objects found by search
    """
    return await _restsearch(db, body)


@router.get(
    "/objects/{objectId}",
    status_code=status.HTTP_200_OK,
    summary="View object details",
)
@alog
async def get_object_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[int, Path(alias="objectId")],
) -> ObjectResponse:
    """View details of a specific object including its attributes and related event.

    args:

    - the user's authentification status

    - the current database

    - the object id

    returns:

    - the details of the object
    """
    return await _get_object_details(db, object_id)


@router.delete(
    "/objects/{objectId}/{hardDelete}",
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusResponse,
    summary="Delete object",
)
@alog
async def delete_object(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[int, Path(alias="objectId")],
    hard_delete: Annotated[bool, Path(alias="hardDelete")],
) -> StandardStatusResponse:
    """Delete a specific object. The hardDelete parameter determines if it's a hard or soft delete.

    args:

    - the user's authentification status

    - the current database

    - the object id

    - hard delete

    returns:

    - the deleted object
    """
    return await _delete_object(db, object_id, hard_delete)


# --- deprecated ---


@router.post(
    "/objects/add/{eventId}/{objectTemplateId}",
    deprecated=True,
    status_code=status.HTTP_201_CREATED,
    response_model=ObjectResponse,
    summary="Add object to event (Deprecated)",
)
@alog
async def add_object_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[int | UUID, Path(alias="eventId")],
    object_template_id: Annotated[int | UUID, Path(alias="objectTemplateId")],
    body: ObjectCreateBody,
) -> ObjectResponse:
    """Deprecated. Add an object to an event using the old route.

    Args:
      auth: user's authentification status
      db: the current database
      event_id: event id
      object_template_id: the object template id
      body: the request body

    Returns:
      the added object
    """
    return await _add_object(db, event_id, object_template_id, body)


@router.get(
    "/objects/view/{objectId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=ObjectResponse,
    summary="View object details (Deprecated)",
)
@alog
async def get_object_details_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[int, Path(alias="objectId")],
) -> ObjectResponse:
    """Deprecated. View details of a specific object using the old route.

    args:

    - the user's authentification status

    - the current database

    - the object id

    returns:

    - the details of the object
    """
    return await _get_object_details(db, object_id)


@router.delete(
    "/objects/delete/{objectId}/{hardDelete}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusResponse,
    summary="Delete object (Deprecated)",
)
@alog
async def delete_object_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[int, Path(alias="objectId")],
    hard_delete: Annotated[bool, Path(alias="hardDelete")],
) -> StandardStatusResponse:
    """
    Deprecated. Delete a specific object using the old route.
    The hardDelete parameter determines if it's a hard or soft delete.

    args:

    - the user's authentification status

    - the current database

    - the object id

    - hard delete

    returns:

    - the deleted object
    """
    return await _delete_object(db, object_id, hard_delete)


# --- endpoint logic ---


@alog
async def _add_object(
    db: Session, event_id: int | UUID, object_template_id: int | UUID, body: ObjectCreateBody
) -> ObjectResponse:
    query_template = select(ObjectTemplate)
    if isinstance(object_template_id, int):
        query_template = query_template.filter(ObjectTemplate.id == object_template_id)
    else:
        query_template = query_template.filter(ObjectTemplate.uuid == object_template_id)

    result_template = await db.execute(query_template)
    template = result_template.scalars().one_or_none()

    query_event = select(Event)
    if isinstance(event_id, int):
        query_event = query_event.filter(Event.id == event_id)
    else:
        query_event = query_event.filter(Event.uuid == event_id)

    result_event = await db.execute(query_event)
    event = result_event.scalars().one_or_none()

    if template is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Object template not found.")
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found.")

    if body.name is None:
        body.name = template.name
    if body.meta_category is None:
        body.meta_category = template.meta_category
    if body.description is None:
        body.description = template.description

    object: Object = Object(
        **body.model_dump(exclude={"Attribute"}),
        template_uuid=template.uuid,
        template_version=template.version,
        event_id=event.id,
        timestamp=int(time()),
    )

    db.add(object)
    await db.flush()
    await db.refresh(object)

    for attr in body.Attribute or []:
        attribute: Attribute = Attribute(
            **attr.model_dump(exclude={"event_id", "object_id", "timestamp"}),
            event_id=int(event_id),
            object_id=object.id,
            timestamp=int(time()) if not attr.timestamp else attr.timestamp,
        )
        db.add(attribute)

    await db.flush()
    await db.refresh(object)

    result = await db.execute(select(Attribute).filter(Attribute.object_id == object.id))
    attributes: Sequence[Attribute] = result.scalars().all()

    attributes_response: list[GetAllAttributesResponse] = [
        GetAllAttributesResponse(**attribute.asdict()) for attribute in attributes
    ]

    object_response: ObjectWithAttributesResponse = ObjectWithAttributesResponse(
        **object.__dict__,
        attributes=attributes_response,
        event=None,
    )

    return ObjectResponse(Object=object_response)


@alog
async def _restsearch(db: Session, body: ObjectSearchBody) -> ObjectSearchResponse:
    if body.return_format is None:
        body.return_format = "json"
    else:
        _check_valid_return_format(return_format=body.return_format)

    objects = await _get_objects_with_filters(db=db, filters=body)

    object_ids = [obj.id for obj in objects]
    result = await db.execute(select(Attribute).filter(Attribute.object_id.in_(object_ids)))
    attributes = result.scalars().all()

    attributes_by_object_id: dict[int, list[Attribute]] = {}
    for attr in attributes:
        if attr.object_id not in attributes_by_object_id:
            attributes_by_object_id[attr.object_id] = []
        attributes_by_object_id[attr.object_id].append(attr)

    objects_data = []
    for obj in objects:
        obj_attributes = attributes_by_object_id.get(obj.id, [])
        attributes_data = [GetAllAttributesResponse.model_validate(attr.asdict()) for attr in obj_attributes]

        obj_data = ObjectWithAttributesResponse(
            **obj.__dict__,
            attributes=attributes_data,
            event=None,
        )
        objects_data.append(obj_data)

    return ObjectSearchResponse(response=objects_data)


@alog
async def _get_object_details(db: Session, object_id: int) -> ObjectResponse:
    object: Object | None = await db.get(Object, object_id)

    if not object:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Object not found.")

    result = await db.execute(select(Attribute).filter(Attribute.object_id == object.id))
    attributes: Sequence[Attribute] = result.scalars().all()

    result2 = await db.execute(
        select(Event).join(Object, Event.id == Object.event_id).filter(Object.id == object_id).limit(1)
    )
    event: Event = result2.scalars().one()

    event_response: ObjectEventResponse = ObjectEventResponse(
        id=event.id, info=event.info, org_id=event.org_id, orgc_id=event.orgc_id
    )

    attributes_response: list[GetAllAttributesResponse] = [
        GetAllAttributesResponse(**attribute.asdict()) for attribute in attributes
    ]
    object_data: ObjectWithAttributesResponse = ObjectWithAttributesResponse(
        **object.__dict__, attributes=attributes_response, event=event_response
    )

    return ObjectResponse(Object=object_data)


@alog
async def _delete_object(db: Session, object_id: int, hard_delete: bool) -> StandardStatusResponse:
    object: Object | None = await db.get(Object, object_id)

    if not object:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Object not found.")

    if hard_delete:
        await db.execute(delete(Attribute).filter(Attribute.object_id == object_id))
        await db.delete(object)
        saved = True
        success = True
        message = "Object has been permanently deleted."
    else:
        object.deleted = True
        saved = True
        success = True
        message = "Object has been soft deleted."

    await db.flush()

    return StandardStatusResponse(
        saved=saved,
        success=success,
        name=object.name,
        message=message,
        url=f"/objects/{object_id}",
    )


@log
def _check_valid_return_format(return_format: str) -> None:
    if return_format not in ["json"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid return format.")


@alog
async def _get_objects_with_filters(db: Session, filters: ObjectSearchBody) -> Sequence[Object]:
    search_body: ObjectSearchBody = filters
    query: Select = select(Object)

    if search_body.object_name:
        query = query.filter(Object.name == search_body.object_name)

    if search_body.object_template_version:
        query = query.filter(Object.template_version == search_body.object_template_version)

    if search_body.event_id:
        query = query.filter(Object.event_id == search_body.event_id)

    if search_body.category:
        query = query.filter(Object.meta_category == search_body.category)

    if search_body.comment:
        query = query.filter(Object.comment.like(f"%{search_body.comment}%"))

    if search_body.first_seen:
        query = query.filter(Object.first_seen == search_body.first_seen)

    if search_body.last_seen:
        query = query.filter(Object.last_seen == search_body.last_seen)

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
        subquery = select(Event.id).filter(Event.timestamp == search_body.event_timestamp)
        query = query.filter(Object.event_id.in_(subquery))

    if search_body.org_id:
        subquery = select(Event.id).filter(Event.org_id == search_body.org_id)
        query = query.filter(Object.event_id.in_(subquery))

    if search_body.uuid:
        query = query.filter(Object.uuid == search_body.uuid)

    if search_body.value1:
        subquery = select(Attribute.object_id).filter(Attribute.value1 == search_body.value1)
        query = query.filter(Object.id.in_(subquery))

    if search_body.value2:
        subquery = select(Attribute.object_id).filter(Attribute.value2 == search_body.value2)
        query = query.filter(Object.id.in_(subquery))

    if search_body.type:
        subquery = select(Attribute.object_id).filter(Attribute.type == search_body.type)
        query = query.filter(Object.id.in_(subquery))

    if search_body.attribute_timestamp:
        subquery = select(Attribute.object_id).filter(Attribute.timestamp == search_body.attribute_timestamp)
        query = query.filter(Object.id.in_(subquery))

    if search_body.to_ids:
        subquery = select(Attribute.object_id).filter(Attribute.to_ids == search_body.to_ids)
        query = query.filter(Object.id.in_(subquery))

    if search_body.published:
        subquery = select(Event.id).filter(Event.published == search_body.published)
        query = query.filter(Object.event_id.in_(subquery))

    if search_body.deleted:
        query = query.filter(Object.deleted == search_body.deleted)

    if search_body.limit:
        query = query.limit(int(search_body.limit))

    result = await db.execute(query)
    return result.scalars().all()
