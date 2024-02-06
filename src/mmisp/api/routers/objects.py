import logging
from datetime import datetime
from typing import Annotated  # , Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.attributes.get_all_attributes_response import GetAllAttributesResponse
from mmisp.api_schemas.events.get_event_response import ObjectEventResponse
from mmisp.api_schemas.objects.add_search_objects_response import (
    ObjectResponse,
    ObjectSearchResponse,
    ObjectWithAttributesSearchResponse,
)
from mmisp.api_schemas.objects.create_object_body import ObjectCreateBody
from mmisp.api_schemas.objects.delete_object_response import ObjectDeleteResponse
from mmisp.api_schemas.objects.get_object_response import (
    ObjectViewResponse,
    ObjectWithAttributesAndEventResponse,
)
from mmisp.api_schemas.objects.search_objects_body import ObjectSearchBody
from mmisp.db.database import get_db
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.object import Object, ObjectTemplate
from mmisp.util.partial import partial

router = APIRouter(tags=["objects"])

logging.basicConfig(
    level=logging.INFO  # todo: remove comment
)  # 'logger.error' for errors on the part of the user, 'logger.exception' for errors on the part of the server
logger = logging.getLogger(__name__)

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
    summary="Add object to event",
    description="Add a new object to a specific event using a template.",
    response_model=partial(ObjectResponse),
    status_code=status.HTTP_201_CREATED,
)
async def add_object(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    body: ObjectCreateBody,
    db: Session = Depends(get_db),
    event_id: str = Path(..., alias="eventId"),
    object_template_id: str = Path(..., alias="objectTemplateId"),
) -> dict:
    return await _add_object(body, db, event_id, object_template_id)


@router.post(
    "/objects/restsearch",
    summary="Search objects",
    description="Search for objects based on various filters.",
    # response_model=partial(ObjectSearchResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_200_OK,
)
async def restsearch(body: ObjectSearchBody, db: Session = Depends(get_db)) -> dict:
    return await _restsearch(body, db)


@router.get(
    "/objects/{objectId}",
    summary="View object details",
    description="View details of a specific object including its attributes and related event.",
    response_model=partial(ObjectViewResponse),
    status_code=status.HTTP_200_OK,
)
async def get_object_details(
    db: Session = Depends(get_db),
    object_id: str = Path(..., alias="objectId"),
) -> dict:
    return await _get_object_details(db, object_id)


@router.delete(
    "/objects/{objectId}/{hardDelete}",
    summary="Delete object",
    description="Delete a specific object. The hardDelete parameter determines if it's a hard or soft delete.",
    response_model=partial(ObjectDeleteResponse),
    status_code=status.HTTP_200_OK,
)
async def delete_object(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Session = Depends(get_db),
    object_id: str = Path(..., alias="objectId"),
    hard_delete: str = Path(..., alias="hardDelete"),
) -> dict:
    return await _delete_object(db, object_id, hard_delete)


# --- deprecated ---


@router.post(
    "/objects/add/{eventId}/{objectTemplateId}",
    deprecated=True,
    summary="Add object to event (Deprecated)",
    description="Deprecated. Add an object to an event using the old route.",
    # response_model=partial(ObjectResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_201_CREATED,
)
async def add_object_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    body: ObjectCreateBody,
    db: Session = Depends(get_db),
    event_id: str = Path(..., alias="eventId"),
    object_template_id: str = Path(..., alias="objectTemplateId"),
) -> dict:
    return await _add_object(body, db, event_id, object_template_id)


@router.get(
    "/objects/view/{objectId}",
    deprecated=True,
    summary="View object details (Deprecated)",
    description="Deprecated. View details of a specific object using the old route.",
    # response_model=partial(ObjectViewResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_200_OK,
)
async def get_object_details_depr(
    db: Session = Depends(get_db),
    object_id: str = Path(..., alias="objectId"),
) -> dict:
    return await _get_object_details(db, object_id)


@router.delete(
    "/objects/delete/{objectId}/{hardDelete}",
    deprecated=True,
    summary="Delete object (Deprecated)",
    description="""
    Deprecated. Delete a specific object using the old route.
    The hardDelete parameter determines if it's a hard or soft delete.""",
    # response_model=partial(ObjectDeleteResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_200_OK,
)
async def delete_object_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Session = Depends(get_db),
    object_id: str = Path(..., alias="objectId"),
    hard_delete: str = Path(..., alias="hardDelete"),
) -> dict:
    return await _delete_object(db, object_id, hard_delete)


# --- endpoint logic ---


async def _add_object(
    body: ObjectCreateBody,
    db: Session,
    event_id: str,
    object_template_id: str,
) -> dict:
    template = db.get(ObjectTemplate, object_template_id)
    if not template:
        logger.error(f"Object template with id '{object_template_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object template not found")

    if not body.name:
        logger.error("Object creation failed: field 'name' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'name' is required.")
    if not body.description:
        logger.error("Object creation failed: field 'description' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'description' is required.")
    if not body.meta_category:
        logger.error("Object creation failed: field 'meta_category' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'meta_category' is required.")
    if not body.distribution:
        logger.error("Object creation failed: field 'distribution' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'distribution' is required.")

    template_uuid = template.uuid
    template_version = template.version

    new_object = Object(
        name=body.name,
        description=body.description,
        template_id=object_template_id,
        event_id=event_id,
        meta_category=body.meta_category,
        distribution=body.distribution,
        deleted=False,
        sharing_group_id=body.sharing_group_id,
        comment=body.comment,
        first_seen=body.first_seen,
        last_seen=body.last_seen,
    )

    try:
        db.add(new_object)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to add new object: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    db.refresh(new_object)
    logger.info(f"New object added: {new_object.id}")

    for attr in body.attributes:
        new_attr = Attribute(
            object_id=new_object.id,
            type=attr.type,
            category=attr.category,
            value=attr.value,
            value1=attr.value1,
            value2=attr.value2,
            to_ids=attr.to_ids,
            disable_correlation=attr.disable_correlation,
            distribution=attr.distribution,
            comment=attr.comment,
        )
        try:
            db.add(new_attr)
        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to add new object: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
            )

    try:
        db.commit()
        logger.info(f"Attributes added to new object: {new_object.id}")
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to add attributes to object: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    attrs = db.query(Attribute).filter(Attribute.object_id == new_object.id).all()
    attributes_list = []

    for attr in attrs:
        object_attr = GetAllAttributesResponse(
            id=str(attr.id),
            uuid=attr.uuid,
            event_id=str(attr.event_id),
            object_id=str(attr.object_id),
            object_relation=attr.object_relation,
            category=attr.category,
            type=attr.type,
            value=attr.value,
            value1=attr.value1,
            value2=attr.value2,
            to_ids=attr.to_ids,
            timestamp=attr.timestamp,
            distribution=attr.distribution,
            sharing_group_id=str(attr.sharing_group_id),
            comment=attr.comment,
            deleted=attr.deleted,
            disable_correlation=attr.disable_correlation,
            first_seen=attr.first_seen,
            last_seen=attr.last_seen,
            event_uuid=attr.event_uuid,
        )
        attributes_list.append(object_attr)

    object_data = ObjectWithAttributesSearchResponse(
        id=str(new_object.id),
        name=new_object.name,
        meta_category=new_object.meta_category,
        description=new_object.description,
        template_uuid=template_uuid,
        template_version=template_version,
        event_id=str(event_id),
        uuid=new_object.uuid,
        timestamp=str(datetime.utcnow),
        distribution=new_object.distribution,
        sharing_group_id=str(new_object.sharing_group_id) if new_object.sharing_group_id is not None else None,
        comment=new_object.comment,
        deleted=new_object.deleted,
        first_seen=new_object.first_seen,
        last_seen=new_object.last_seen,
        attributes=attributes_list,
    )

    return ObjectResponse(object=object_data)


async def _restsearch(body: ObjectSearchBody, db: Session) -> dict:
    for field, value in body.dict().items():
        db_object = db.query(Object).filter(getattr(Object, field) == value).all()

        # todo: not all fields in 'ObjectSearchBody' are taken into account yet

    response_objects = []

    for obj in db_object:
        attributes_list = []
        for attr in obj.attributes:
            object_attr = GetAllAttributesResponse(
                id=str(attr.id),
                uuid=attr.uuid,
                event_id=str(attr.event_id),
                object_id=str(attr.object_id),
                object_relation=attr.object_relation,
                category=attr.category,
                type=attr.type,
                value=attr.value,
                value1=attr.value1,
                value2=attr.value2,
                to_ids=attr.to_ids,
                timestamp=attr.timestamp,
                distribution=attr.distribution,
                sharing_group_id=str(attr.sharing_group_id) if attr.sharing_group_id is not None else None,
                comment=attr.comment,
                deleted=attr.deleted,
                disable_correlation=attr.disable_correlation,
                first_seen=attr.first_seen,
                last_seen=attr.last_seen,
                event_uuid=attr.event_uuid,
            )
            attributes_list.append(object_attr)

        response_object = ObjectWithAttributesSearchResponse(
            id=str(obj.id),
            description=obj.description,
            name=obj.name,
            meta_category=obj.meta_category,
            distribution=str(obj.distribution),
            template_uuid=str(obj.template_id),
            event_id=str(obj.event_id),
            uuid=obj.uuid,
            timestamp=str(datetime.utcnow),
            sharing_group_id=str(obj.sharing_group_id) if obj.sharing_group_id is not None else None,
            comment=obj.comment,
            first_seen=obj.first_seen,
            last_seen=obj.last_seen,
            attributes=attributes_list,
        )
        response_objects.append(response_object)

    return ObjectSearchResponse(response=[{"object": res_obj} for res_obj in response_objects])


async def _get_object_details(
    db: Session,
    object_id: str,
) -> dict:
    db_object = db.get(Object, object_id)
    if not db_object:
        logger.error(f"Object with id '{object_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")

    db_attributes = db.query(Attribute).filter(Attribute.object_id == db_object.id).all()

    object_attributes = [
        GetAllAttributesResponse(
            id=str(attr.id),
            uuid=attr.uuid,
            event_id=str(attr.event_id),
            object_id=str(attr.object_id),
            object_relation=attr.object_relation,
            category=attr.category,
            type=attr.type,
            value=attr.value,
            value1=attr.value1,
            value2=attr.value2,
            to_ids=attr.to_ids,
            timestamp=attr.timestamp,
            distribution=attr.distribution,
            sharing_group_id=str(attr.sharing_group_id) if attr.sharing_group_id is not None else None,
            comment=attr.comment,
            deleted=attr.deleted,
            disable_correlation=attr.disable_correlation,
            first_seen=attr.first_seen,
            last_seen=attr.last_seen,
            event_uuid=attr.event_uuid,
        )
        for attr in db_attributes
    ]

    db_event = db.query(Event).join(Object, Event.id == Object.event_id).filter(Object.id == object_id).first()
    event_response = ObjectEventResponse(
        id=str(db_event.id), info=db_event.info, org_id=str(db_event.org_id), orgc_id=str(db_event.orgc_id)
    )

    template = db.get(ObjectTemplate, db_object.template_id)
    if not template:
        logger.error(f"Object template with id '{db_object.template_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object template not found")

    template_uuid = template.uuid
    template_version = template.version

    response_object = ObjectWithAttributesAndEventResponse(
        id=str(db_object.id),
        name=db_object.name,
        description=db_object.description,
        meta_category=db_object.meta_category,
        event_id=str(db_object.event_id),
        distribution=str(db_object.distribution),
        template_uuid=template_uuid,
        template_version=template_version,
        uuid=db_object.uuid,
        timestamp=str(datetime.utcnow),
        sharing_group_id=str(db_object.sharing_group_id) if db_object.sharing_group_id is not None else None,
        comment=db_object.comment,
        deleted=db_object.deleted,
        first_seen=db_object.first_seen,
        last_seen=db_object.last_seen,
        attributes=object_attributes,
        event=event_response,
    )

    return ObjectViewResponse(object=response_object)


async def _delete_object(
    db: Session,
    object_id: str,
    hard_delete: str,
) -> dict:
    db_object = db.get(Object, object_id)
    if not db_object:
        logger.error(f"Object with id '{object_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found")

    if hard_delete.lower() == "true":
        db.delete(db_object)
        try:
            db.commit()
            logger.info(f"Hard deleted object with id '{object_id}'.")
        except Exception as e:
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
        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to soft delete object with id '{object_id}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
            )
        message = "Object has been soft deleted."
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid hardDelete parameter.")

    return ObjectDeleteResponse(
        saved=True, success=True, name=db_object.name, message=message, url=f"/objects/{object_id}"
    )


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
