from time import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, status
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
from mmisp.db.database import get_db
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.object import Object, ObjectTemplate
from mmisp.util.partial import partial
from mmisp.util.request_validations import check_existence_and_raise

router = APIRouter(tags=["objects"])


# sorted according to CRUD


@router.post(
    "/objects/{eventId}/{objectTemplateId}",
    status_code=status.HTTP_201_CREATED,
    response_model=partial(ObjectResponse),
    summary="Add object to event",
    description="Add a new object to a specific event using a template.",
)
async def add_object(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    object_template_id: Annotated[str, Path(..., alias="objectTemplateId")],
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
async def restsearch(db: Annotated[Session, Depends(get_db)], body: ObjectSearchBody) -> dict[str, Any]:
    return await _restsearch(db, body)


@router.get(
    "/objects/{objectId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(ObjectResponse),
    summary="View object details",
    description="View details of a specific object including its attributes and related event.",
)
async def get_object_details(
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[str, Path(..., alias="objectId")],
) -> dict[str, Any]:
    return await _get_object_details(db, object_id)


@router.delete(
    "/objects/{objectId}/{hardDelete}",
    status_code=status.HTTP_200_OK,
    response_model=partial(StandardStatusResponse),
    summary="Delete object",
    description="Delete a specific object. The hardDelete parameter determines if it's a hard or soft delete.",
)
async def delete_object(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[str, Path(..., alias="objectId")],
    hard_delete: Annotated[bool, Path(..., alias="hardDelete")],
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
async def add_object_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    object_template_id: Annotated[str, Path(..., alias="objectTemplateId")],
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
async def get_object_details_depr(
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[str, Path(..., alias="objectId")],
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
async def delete_object_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[str, Path(..., alias="objectId")],
    hard_delete: Annotated[bool, Path(..., alias="hardDelete")],
) -> dict[str, Any]:
    return await _delete_object(db, object_id, hard_delete)


# --- endpoint logic ---


async def _add_object(db: Session, event_id: str, object_template_id: str, body: ObjectCreateBody) -> dict[str, Any]:
    template: ObjectTemplate = check_existence_and_raise(
        db=db,
        model=ObjectTemplate,
        value=object_template_id,
        column_name="id",
        error_detail="Object template not found.",
    )
    check_existence_and_raise(db=db, model=Event, value=event_id, column_name="id", error_detail="Event not found.")

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
        GetAllAttributesResponse(**attribute.__dict__) for attribute in attributes
    ]

    object_response: ObjectWithAttributesResponse = ObjectWithAttributesResponse(
        **object.__dict__,
        attributes=attributes_response,
        event=None,
    )

    return ObjectResponse(object=object_response)


async def _restsearch(db: Session, body: ObjectSearchBody) -> dict[str, Any]:
    for field, value in body.dict().items():
        objects: list[Object] = db.query(Object).filter(getattr(Object, field) == value).all()

        # todo: not all fields in 'ObjectSearchBody' are taken into account yet

    objects_data: list[ObjectWithAttributesResponse] = [
        ObjectWithAttributesResponse(**object.__dict__, attributes=object.attributes, event=None) for object in objects
    ]

    return ObjectSearchResponse(response=[{"object": object_data} for object_data in objects_data])


async def _get_object_details(db: Session, object_id: str) -> dict[str, Any]:
    object: Object = check_existence_and_raise(
        db=db, model=Object, value=object_id, column_name="id", error_detail="Object not found."
    )
    attributes: list[Attribute] = db.query(Attribute).filter(Attribute.object_id == object.id).all()
    event: Event = db.query(Event).join(Object, Event.id == Object.event_id).filter(Object.id == object_id).first()
    event_response: ObjectEventResponse = ObjectEventResponse(
        id=str(event.id), info=event.info, org_id=str(event.org_id), orgc_id=str(event.orgc_id)
    )

    attributes_response: list[GetAllAttributesResponse] = [
        GetAllAttributesResponse(**attribute.__dict__) for attribute in attributes
    ]
    object_data: ObjectWithAttributesResponse = ObjectWithAttributesResponse(
        **object.__dict__, attributes=attributes_response, event=event_response
    )

    return ObjectResponse(object=object_data)


async def _delete_object(db: Session, object_id: str, hard_delete: bool) -> dict[str, Any]:
    object: Object = check_existence_and_raise(
        db=db, model=Object, value=object_id, column_name="id", error_detail="Object not found."
    )
    saved: bool = False
    success: bool = False

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


#####################################################################
#####################################################################
###                                                               ###
###     Search logic for all fields in ObjectSearchBody (wip)     ###
###                                                               ###
#####################################################################
#####################################################################


# def _build_query(db: Session, search_body: ObjectSearchBody) -> list[Object]:
#     query = db.query(Object)

#     if search_body.object_name:
#         query = query.filter(Object.name == search_body.object_name)

#     if search_body.object_template_uuid:
#         query = query.filter(Object.template_id == search_body.object_template_uuid)

#     if search_body.eventid:
#         query = query.filter(Object.event_id == search_body.eventid)

#     if search_body.meta_category:
#         query = query.filter(Object.meta_category == search_body.meta_category)

#     if search_body.distribution:
#         query = query.filter(Object.distribution == search_body.distribution)

#     if search_body.sharing_group_id:
#         query = query.filter(Object.sharing_group_id == search_body.sharing_group_id)

#     if search_body.comment:
#         query = query.filter(Object.comment.like(f"%{search_body.comment}%"))

#     if search_body.first_seen:
#         query = query.filter(Object.first_seen == search_body.first_seen)

#     if search_body.last_seen:
#         query = query.filter(Object.last_seen == search_body.last_seen)

#     if search_body.page:
#         query = query.offset((search_body.page - 1) * search_body.limit)

#     if search_body.limit:
#         query = query.limit(search_body.limit)

#     if search_body.quickFilter:
#         query = query.filter(
#             or_(
#                 Object.name.like(f"%{search_body.quickFilter}%"),
#                 Object.description.like(f"%{search_body.quickFilter}%"),
#             )
#         )

#     if search_body.timestamp:
#         query = query.filter(Object.timestamp == search_body.timestamp)

#     if search_body.eventinfo:
#         query = query.join(Event).filter(Event.info.like(f"%{search_body.eventinfo}%"))

#     if search_body.ignore:
#         # Logic to ignore certain objects based on the 'ignore' field
#         pass

#     if search_body.from_:
#         query = query.filter(Object.timestamp >= search_body.from_)

#     if search_body.to:
#         query = query.filter(Object.timestamp <= search_body.to)

#     if search_body.date:
#         # Logic to filter based on a specific date
#         pass

#     if search_body.tags:
#         # Logic to filter based on tags, possibly via a relation
#         pass

#     if search_body.last:
#         # Logic to consider the 'last' filter
#         pass

#     if search_body.event_timestamp:
#         # Logic to filter based on the event timestamp
#         pass

#     if search_body.publish_timestamp:
#         # Logic to filter based on the publication timestamp
#         pass

#     if search_body.org:
#         # Logic to filter based on organization
#         pass

#     if search_body.uuid:
#         query = query.filter(Object.uuid == search_body.uuid)

#     if search_body.value1:
#         # Logic to filter based on 'value1'
#         pass

#     if search_body.value2:
#         # Logic to filter based on 'value2'
#         pass

#     if search_body.type:
#         # Logic to filter based on type
#         pass

#     if search_body.category:
#         # Logic to filter based on category
#         pass

#     if search_body.object_relation:
#         # Logic to filter based on object relation
#         pass

#     if search_body.attribute_timestamp:
#         # Logic to filter based on the attribute timestamp
#         pass

#     if search_body.first_seen:
#         # Logic to filter based on 'first_seen'
#         pass

#     if search_body.last_seen:
#         # Logic to filter based on 'last_seen'
#         pass

#     if search_body.comment:
#         # Logic to filter based on comments
#         pass

#     if search_body.to_ids:
#         # Logic to filter based on the 'to_ids' field
#         pass

#     if search_body.published:
#         # Logic to filter based on whether the object is published
#         pass

#     if search_body.deleted:
#         query = query.filter(Object.deleted == search_body.deleted)

#     if search_body.withAttachments:
#         # Logic to consider attachments
#         pass

#     if search_body.enforceWarninglist:
#         # Logic to consider the warning list
#         pass

#     if search_body.includeAllTags:
#         # Logic to include all tags
#         pass

#     if search_body.includeEventUuid:
#         # Logic to include the event UUID
#         pass

#     if search_body.include_event_uuid:
#         # Logic to include the event UUID (alternative field)
#         pass

#     if search_body.includeEventTags:
#         # Logic to include event tags
#         pass

#     if search_body.includeProposals:
#         # Logic to include proposals
#         pass

#     if search_body.includeWarninglistHits:
#         # Logic to include warning list hits
#         pass

#     if search_body.includeContext:
#         # Logic to include context
#         pass

#     if search_body.includeSightings:
#         # Logic to include sightings
#         pass

#     if search_body.includeSightingdb:
#         # Logic to include the sighting database
#         pass

#     if search_body.includeCorrelations:
#         # Logic to include correlations
#         pass

#     if search_body.includeDecayScore:
#         # Logic to include the decay score
#         pass

#     if search_body.includeFullModel:
#         # Logic to include the full model
#         pass

#     if search_body.allow_proposal_blocking:
#         # Logic to consider proposal blocking
#         pass

#     if search_body.metadata:
#         # Logic to consider metadata
#         pass

#     if search_body.attackGalaxy:
#         # Logic to filter based on 'attackGalaxy'
#         pass

#     if search_body.excludeDecayed:
#         # Logic to exclude decayed objects
#         pass

#     if search_body.decayingModel:
#         # Logic to consider the decaying model
#         pass

#     if search_body.modelOverrides:
#         # Logic to consider model overrides
#         pass

#     if search_body.score:
#         # Logic to filter based on a score
#         pass

#     if search_body.returnFormat:
#         # Logic to adjust the return format, if necessary
#         pass

#     return query.all()
