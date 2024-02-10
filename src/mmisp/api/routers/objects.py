import logging
import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.attributes.get_all_attributes_response import GetAllAttributesResponse
from mmisp.api_schemas.events.get_event_response import ObjectEventResponse
from mmisp.api_schemas.objects.create_object_body import ObjectCreateBody
from mmisp.api_schemas.objects.delete_object_response import ObjectDeleteResponse
from mmisp.api_schemas.objects.get_object_response import (
    ObjectResponse,
    ObjectSearchResponse,
    ObjectWithAttributesResponse,
)
from mmisp.api_schemas.objects.search_objects_body import ObjectSearchBody
from mmisp.db.database import get_db
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.object import Object, ObjectTemplate
from mmisp.util.partial import partial
from mmisp.util.request_validations import check_existence_and_raise

router = APIRouter(tags=["objects"])
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


# sorted according to CRUD


@router.post(
    "/objects/{eventId}/{objectTemplateId}",
    status_code=status.HTTP_201_CREATED,
    response_model=partial(ObjectResponse),
    summary="Add object to event",
    description="Add a new object to a specific event using a template.",
)
async def add_object(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    object_template_id: Annotated[str, Path(..., alias="objectTemplateId")],
    body: ObjectCreateBody,
) -> dict:
    return await _add_object(db, event_id, object_template_id, body)


@router.post(
    "/objects/restsearch",
    status_code=status.HTTP_200_OK,
    response_model=partial(ObjectSearchResponse),
    summary="Search objects",
    description="Search for objects based on various filters.",
)
async def restsearch(db: Annotated[Session, Depends(get_db)], body: ObjectSearchBody) -> dict:
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
) -> dict:
    return await _get_object_details(db, object_id)


@router.delete(
    "/objects/{objectId}/{hardDelete}",
    status_code=status.HTTP_200_OK,
    response_model=partial(ObjectDeleteResponse),
    summary="Delete object",
    description="Delete a specific object. The hardDelete parameter determines if it's a hard or soft delete.",
)
async def delete_object(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[str, Path(..., alias="objectId")],
    hard_delete: Annotated[str, Path(..., alias="hardDelete")],
) -> dict:
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
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    object_template_id: Annotated[str, Path(..., alias="objectTemplateId")],
    body: ObjectCreateBody,
) -> dict:
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
) -> dict:
    return await _get_object_details(db, object_id)


@router.delete(
    "/objects/delete/{objectId}/{hardDelete}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(ObjectDeleteResponse),
    summary="Delete object (Deprecated)",
    description="""
    Deprecated. Delete a specific object using the old route.
    The hardDelete parameter determines if it's a hard or soft delete.""",
)
async def delete_object_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    object_id: Annotated[str, Path(..., alias="objectId")],
    hard_delete: Annotated[str, Path(..., alias="hardDelete")],
) -> dict:
    return await _delete_object(db, object_id, hard_delete)


# --- endpoint logic ---


async def _add_object(db: Session, event_id: str, object_template_id: str, body: ObjectCreateBody) -> dict:
    template: ObjectTemplate = check_existence_and_raise(
        db, ObjectTemplate, object_template_id, "object_template_id", "Object template not found"
    )
    check_existence_and_raise(db, Event, event_id, "event_id", "Event not found")

    new_object_data = {
        **body.dict(exclude={"attributes"}),
        "template_id": int(object_template_id) if object_template_id is not None else None,
        "template_name": template.name if template is not None else None,
        "template_uuid": template.uuid if template is not None else None,
        "template_version": template.version if template is not None else None,
        "template_description": template.description if template is not None else None,
        "event_id": int(event_id) if event_id is not None else None,
        "timestamp": _create_timestamp(),
    }
    new_object = Object(**new_object_data)

    try:
        db.add(new_object)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Failed to add new object: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    db.refresh(new_object)
    logger.info(f"New object added: {new_object.id}")

    try:
        attributes_data = [
            {**attr.dict(), "object_id": new_object.id, "timestamp": _create_timestamp()} for attr in body.attributes
        ]
        db.bulk_insert_mappings(Attribute, attributes_data)
        db.commit()
        logger.info(f"Attributes added to new object: {new_object.id}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Failed to add attributes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    db_attributes: list[Attribute] = db.query(Attribute).filter(Attribute.object_id == new_object.id).all()

    return ObjectResponse(object=_prepare_object_response(new_object, db_attributes, event_response=None))


async def _restsearch(db: Session, body: ObjectSearchBody) -> dict:
    for field, value in body.dict().items():
        db_objects: list[Object] = db.query(Object).filter(getattr(Object, field) == value).all()

        # todo: not all fields in 'ObjectSearchBody' are taken into account yet

    response_objects = [_prepare_object_response(obj, obj.attributes, event_response=None) for obj in db_objects]

    return ObjectSearchResponse(response=[{"object": res_obj} for res_obj in response_objects])


async def _get_object_details(db: Session, object_id: str) -> dict:
    db_object: Object = check_existence_and_raise(db, Object, object_id, "object_id", "Object not found")

    db_attributes: list[Attribute] = db.query(Attribute).filter(Attribute.object_id == db_object.id).all()
    db_event: Event = db.query(Event).join(Object, Event.id == Object.event_id).filter(Object.id == object_id).first()

    event_response: ObjectEventResponse = ObjectEventResponse(
        id=str(db_event.id), info=db_event.info, org_id=str(db_event.org_id), orgc_id=str(db_event.orgc_id)
    )

    return ObjectResponse(object=_prepare_object_response(db_object, db_attributes, event_response))


async def _delete_object(db: Session, object_id: str, hard_delete: str) -> dict:
    db_object: Object = check_existence_and_raise(db, Object, object_id, "object_id", "Object not found")

    if hard_delete.lower() == "true":
        db.query(Attribute).filter(Attribute.object_id == object_id).delete(synchronize_session=False)
        db.delete(db_object)
        try:
            db.commit()
            logger.info(f"Hard deleted object with id '{object_id}'.")
        except SQLAlchemyError as e:
            db.rollback()
            logger.exception(f"Failed to hard delete object with id '{object_id}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
            )
        message = "Object has been permanently deleted."
    elif hard_delete.lower() == "false":
        db_object.deleted = True
        try:
            db.commit()
            logger.info(f"Soft deleted object with id '{object_id}'.")
        except SQLAlchemyError as e:
            db.rollback()
            logger.exception(f"Failed to soft delete object with id '{object_id}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
            )
        message = "Object has been soft deleted."
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 'hardDelete' parameter.")

    return ObjectDeleteResponse(
        saved=True,
        success=True,
        name=db_object.name,
        message=message,
        url=f"/objects/{object_id}",
    )


def _prepare_attributes_response(attributes: list[Attribute]) -> list[GetAllAttributesResponse]:
    return [
        GetAllAttributesResponse(
            id=str(attr.id),
            uuid=attr.uuid,
            event_id=str(attr.event_id) if attr.event_id is not None else None,
            object_id=str(attr.object_id) if attr.object_id is not None else None,
            object_relation=attr.object_relation,
            category=attr.category,
            type=attr.type,
            value=attr.value,
            value1=attr.value1,
            value2=attr.value2,
            to_ids=attr.to_ids,
            timestamp=str(attr.timestamp) if attr.timestamp is not None else None,
            distribution=str(attr.distribution) if attr.distribution is not None else None,
            sharing_group_id=str(attr.sharing_group_id) if attr.sharing_group_id is not None else None,
            comment=attr.comment,
            deleted=attr.deleted,
            disable_correlation=attr.disable_correlation,
            first_seen=str(attr.first_seen) if attr.first_seen is not None else None,
            last_seen=str(attr.last_seen) if attr.last_seen is not None else None,
        )
        for attr in attributes
    ]


def _prepare_object_response(
    object: Object, attributes: list[Attribute], event_response: ObjectEventResponse
) -> ObjectWithAttributesResponse:
    attributes_response = _prepare_attributes_response(attributes)
    object_data = ObjectWithAttributesResponse(
        id=str(object.id),
        uuid=object.uuid,
        name=object.name,
        meta_category=object.meta_category,
        description=object.description,
        template_id=str(object.template_id) if object.template_id is not None else None,
        template_uuid=object.template_uuid,
        template_version=str(object.template_version) if object.template_version is not None else None,
        event_id=str(object.event_id) if object.event_id is not None else None,
        timestamp=str(object.timestamp) if object.timestamp is not None else None,
        distribution=str(object.distribution) if object.distribution is not None else None,
        sharing_group_id=str(object.sharing_group_id) if object.sharing_group_id is not None else None,
        comment=object.comment if object.comment is not None else None,
        deleted=object.deleted,
        first_seen=str(object.first_seen) if object.first_seen is not None else None,
        last_seen=str(object.last_seen) if object.last_seen is not None else None,
        attributes=attributes_response,
        event=event_response,
    )
    return object_data


def _create_timestamp() -> int:
    return int(time.time())


#####################################################################
#####################################################################
###                                                               ###
###     Search logic for all fields in ObjectSearchBody (wip)     ###
###                                                               ###
#####################################################################
#####################################################################


# def build_query(db: Session, search_body: ObjectSearchBody) -> list[Object]:
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
