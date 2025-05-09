import logging
import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.attributes import (
    AddAttributeAttributes,
    AddAttributeBody,
    AddAttributeResponse,
    AddRemoveTagAttributeResponse,
    DeleteAttributeResponse,
    EditAttributeAttributes,
    EditAttributeBody,
    EditAttributeResponse,
    GetAllAttributesResponse,
    GetAttributeAttributes,
    GetAttributeResponse,
    GetAttributeStatisticsCategoriesResponse,
    GetAttributeStatisticsTypesResponse,
    GetAttributeTag,
    GetDescribeTypesAttributes,
    GetDescribeTypesResponse,
    SearchAttributesBody,
    SearchAttributesEvent,
    SearchAttributesObject,
    SearchAttributesResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.event import Event
from mmisp.db.models.tag import Tag
from mmisp.db.models.user import User
from mmisp.lib.attribute_search_filter import get_search_filters
from mmisp.lib.distribution import AttributeDistributionLevels
from mmisp.lib.logger import alog, log

from ..workflow import execute_workflow

logger = logging.getLogger("mmisp")

router = APIRouter(tags=["attributes"])


@router.post(
    "/attributes/restSearch",
    status_code=status.HTTP_200_OK,
    summary="Search attributes",
)
@alog
async def rest_search_attributes(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: SearchAttributesBody,
) -> SearchAttributesResponse:
    """Search for attributes based on various filters.

    args:
        auth: the user's authentification status
        db: the current database
        body: the search body

    returns:
        the attributes the search finds
    """
    return await _rest_search_attributes(db, body, auth.user)


@router.post(
    "/attributes/{eventId}",
    status_code=status.HTTP_200_OK,
    summary="Add new attribute",
)
@alog
async def add_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[uuid.UUID | int, Path(alias="eventId")],
    body: AddAttributeBody,
) -> AddAttributeResponse:
    """Add a new attribute with the given details.

    args:
        auth: the user's authentification status
        db: the current database
        event_id: the ID or UUID of the event
        body: the body for adding an attribute

    returns:
        the response of the added attribute from the api
    """
    return await _add_attribute(db, event_id, body, auth.user)


@router.get(
    "/attributes/describeTypes",
    status_code=status.HTTP_200_OK,
    summary="Get all attribute describe types",
)
@alog
async def get_attributes_describe_types(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
) -> GetDescribeTypesResponse:
    """Retrieve a list of all available attribute types and categories.

    args:
        auth: the user's authentification status

    returns:
        the attributes describe types
    """
    return GetDescribeTypesResponse(result=GetDescribeTypesAttributes())


@router.get(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    summary="Get attribute details",
)
@alog
async def get_attribute_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int | uuid.UUID, Path(alias="attributeId")],
) -> GetAttributeResponse:
    """Retrieve details of a specific attribute by either by its ID or UUID.

    args:
        auth: the user's authentification status
        db: the current database
        attribute_id: the ID or UUID of the attribute

    returns:
        the attribute details
    """
    return await _get_attribute_details(db, attribute_id, auth.user)


@router.put(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    summary="Update an attribute",
)
@alog
async def update_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int | uuid.UUID, Path(alias="attributeId")],
    body: EditAttributeBody,
) -> EditAttributeResponse:
    """Update an existing attribute by its ID.

    args:
        auth: the user's authentification status
        db: the current database
        attribute_id: the ID or UUID of the attribute
        body: the body for editing the attribute

    returns:
        the response from the api for the edit/update request
    """
    return await _update_attribute(db, attribute_id, body, auth.user)


@router.delete(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteAttributeResponse,
    summary="Delete an Attribute",
)
@alog
async def delete_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int | uuid.UUID, Path(alias="attributeId")],
    hard: bool = False,
) -> DeleteAttributeResponse:
    """Delete an attribute by either by its ID or UUID.

    args:
        auth: the user's authentification status
        db: the current database
        attribute_id: the ID or UUID of the attribute

    returns:
        the response from the api for the delete request
    """
    return await _delete_attribute(db, attribute_id, hard, auth.user)


@router.get(
    "/attributes",
    status_code=status.HTTP_200_OK,
    summary="Get all Attributes",
)
@alog
async def get_attributes(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> list[GetAllAttributesResponse]:
    """Retrieve a list of all attributes.

    args:
        auth: the user's authentification status

    returns:
        the list of all attributes
    """
    return await _get_attributes(db, auth.user)


@router.get(
    "/attributes/attributeStatistics/type/{percentage}",
    status_code=status.HTTP_200_OK,
    summary="Get attribute statistics",
    response_model_exclude_unset=True,
)
@alog
async def get_attributes_type_statistics(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    percentage: bool,
) -> GetAttributeStatisticsTypesResponse:  # type: ignore
    """Get the count/percentage of attributes per category/type.

    args:
        auth: the user's authentification status
        db: the current database
        percentage: percentage request or not

    returns:
        the attributes statistics for one category/type
    """
    return await _get_attribute_type_statistics(db, percentage, auth.user)


@router.get(
    "/attributes/attributeStatistics/category/{percentage}",
    status_code=status.HTTP_200_OK,
    summary="Get attribute statistics",
    response_model_exclude_unset=True,
)
@alog
async def get_attributes_category_statistics(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    percentage: bool,
) -> GetAttributeStatisticsCategoriesResponse:  # type: ignore
    """Get the count/percentage of attributes per category/type.

    args:
        auth: the user's authentification status
        db: the current database
        percentage: percentage request or not

    returns:
        the attributes statistics for one category/type
    """
    return await _get_attribute_category_statistics(db, percentage)


@router.post(
    "/attributes/restore/{attributeId}",
    status_code=status.HTTP_200_OK,
    summary="Restore an attribute",
)
@alog
async def restore_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int | uuid.UUID, Path(alias="attributeId")],
) -> GetAttributeResponse:
    """Restore an attribute either by its ID or UUID.

    args:
        auth: the user's authentification status
        db: the current database
        attribute_id: the ID or UUID of the attribute

    returns:
        the restored attribute
    """
    return await _restore_attribute(db, attribute_id, auth.user)


@router.post(
    "/attributes/addTag/{attributeId}/{tagId}/local:{local}",
    status_code=status.HTTP_200_OK,
    summary="Add tag to attribute",
)
@alog
async def add_tag_to_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.TAGGER]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int | uuid.UUID, Path(alias="attributeId")],
    tag_id: Annotated[str, Path(alias="tagId")],
    local: str,
) -> AddRemoveTagAttributeResponse:
    """Add a tag to an attribute by there IDs.

    args:
        auth: the user's authentification status
        db: the current database
        attribute_id: the ID or UUID of the attribute
        tag_id: the ID of the tag
        local: "1" for local

    returns:
        the response from the api for adding a tag to an attribute
    """
    return await _add_tag_to_attribute(db, attribute_id, tag_id, local, auth.user)


@router.post(
    "/attributes/removeTag/{attributeId}/{tagId}",
    status_code=status.HTTP_200_OK,
    summary="Remove tag from attribute",
)
@alog
async def remove_tag_from_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.TAGGER]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int | uuid.UUID, Path(alias="attributeId")],
    tag_id: Annotated[str, Path(alias="tagId")],
) -> AddRemoveTagAttributeResponse:
    """Remove a tag from an attribute by there IDs.

    args:
        auth: the user's authentification status
        db: the current database
        attribute_id: the ID or UUID of the attribute
        tag_id: the ID of the tag

    returns:
        the response from the api for removing a tag to an attribute
    """
    return await _remove_tag_from_attribute(db, attribute_id, tag_id, auth.user)


# --- deprecated ---


@router.post(
    "/attributes/add/{eventId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=AddAttributeResponse,
    summary="Add new attribute (Deprecated)",
)
@alog
async def add_attribute_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[int, Path(alias="eventId")],
    body: AddAttributeBody,
) -> AddAttributeResponse:
    """Deprecated. Add a new attribute with the given details using the old route.

    args:

    the user's authentification status

    the current database

    the id of the event

    the body

    returns:

    the attribute
    """
    return await _add_attribute(db, event_id, body, auth.user)


@router.get(
    "/attributes/view/{attributeId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=GetAttributeResponse,
    summary="Get attribute details (Deprecated)",
)
@alog
async def get_attribute_details_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int, Path(alias="attributeId")],
) -> GetAttributeResponse:
    """Deprecated. Retrieve details of a specific attribute by its ID using the old route.

    args:

    the user's authentification status

    the current database

    the id of the attribute

    returns:

    the details of an attribute
    """
    return await _get_attribute_details(db, attribute_id, auth.user)


@router.put(
    "/attributes/edit/{attributeId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=EditAttributeResponse,
    summary="Update an attribute (Deprecated)",
)
@alog
async def update_attribute_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int, Path(alias="attributeId")],
    body: EditAttributeBody,
) -> EditAttributeResponse:
    """Deprecated. Update an existing attribute by its ID using the old route.

    args:

    the user's authentification status

    the current database

    the id of the attribute

    the body

    returns:

    the updated version af an attribute
    """
    return await _update_attribute(db, attribute_id, body, auth.user)


@router.delete(
    "/attributes/delete/{attributeId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
)
@alog
async def delete_attribute_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int, Path(alias="attributeId")],
    hard: bool = False,
) -> DeleteAttributeResponse:
    """Deprecated. Delete an attribute by its ID using the old route.

    args:

    the user's authentification status

    the current database

    the id of the attribute

    returns:

    the response from the api for the deleting request
    """
    return await _delete_attribute(db, attribute_id, hard, auth.user)


# --- endpoint logic ---


@alog
async def _add_attribute(
    db: Session, event_id: int | uuid.UUID, body: AddAttributeBody, user: User | None
) -> AddAttributeResponse:
    if isinstance(event_id, uuid.UUID):
        event = await _get_event_by_uuid(event_id, db)
    else:
        event = await db.get(Event, event_id)

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if not event.can_edit(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can not edit event")
    if not body.value:
        if not body.value1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'value' or 'value1' is required")
    if not body.type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'type' is required")
    if body.type not in GetDescribeTypesAttributes().types:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid 'type'")
    if body.category:
        if body.category not in GetDescribeTypesAttributes().categories:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid 'category'")

    new_attribute = Attribute(
        **{
            **body.model_dump(),
            "event_id": int(event.id),
            "category": body.category
            if body.category is not None
            else GetDescribeTypesAttributes().sane_defaults[body.type]["default_category"],
            "value": body.value if body.value is not None else body.value1,
            "value1": body.value1 if body.value1 is not None else body.value,
            "value2": body.value2 if body.value2 is not None else "",
        }
    )

    db.add(new_attribute)
    await db.flush()

    await db.refresh(new_attribute)

    await execute_workflow("attribute-after-save", db, new_attribute)

    setattr(event, "attribute_count", event.attribute_count + 1)

    attribute_data = _prepare_attribute_response_add(new_attribute)

    return AddAttributeResponse(Attribute=attribute_data)


@alog
async def _get_attribute_details(db: Session, attribute_id: int | uuid.UUID, user: User | None) -> GetAttributeResponse:
    attribute: Attribute | None  # I have no idea, why this type declaration is necessary

    attribute = await _get_attribute(db, attribute_id, load_sharing_group=True)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if not attribute.can_access(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    attribute_data = await _prepare_get_attribute_details_response(db, attribute_id, attribute)

    return GetAttributeResponse(Attribute=attribute_data)


@alog
async def _update_attribute(
    db: Session, attribute_id: int | uuid.UUID, body: EditAttributeBody, user: User | None
) -> EditAttributeResponse:
    attribute = await _get_attribute(db, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if not attribute.can_edit(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    # first_seen/last_seen being an empty string is accepted by legacy MISP
    # and implies "field is not set".
    payload = body.model_dump(exclude_unset=True)
    for seen in ["first_seen", "last_seen"]:
        if seen in payload and not payload[seen]:
            payload[seen] = None

    if "distribution" in payload and user is not None:
        sharing_group_id: int | None = payload.get("sharing_group_id", None)
        if payload["distribution"] == AttributeDistributionLevels.SHARING_GROUP:
            # sharing group_id can be anything > 0
            if sharing_group_id not in user.org._sharing_group_ids:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif payload["distribution"] == AttributeDistributionLevels.INHERIT_EVENT:
            event_sharing_group_id = attribute.event.sharing_group_id

            if sharing_group_id is None:
                sharing_group_id = event_sharing_group_id
            # sharing_group_id must be the same as event
            if sharing_group_id != event_sharing_group_id:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)

            payload["sharing_group_id"] = sharing_group_id
        else:
            # sharing_group_id must be 0
            if sharing_group_id is None:
                payload["sharing_group_id"] = 0
            elif sharing_group_id > 0:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)
            payload["sharing_group_id"] = 0

    attribute.patch(**payload)
    attribute.timestamp = datetime.now()

    await execute_workflow("attribute-after-save", db, attribute)

    await db.flush()
    await db.refresh(attribute)

    attribute_data = await _prepare_edit_attribute_response(db, attribute_id, attribute)

    return EditAttributeResponse(Attribute=attribute_data)


@alog
async def _delete_attribute(
    db: Session, attribute_id: int | uuid.UUID, hard: bool, user: User | None
) -> DeleteAttributeResponse:
    attribute: Attribute | None  # I have no idea, why this type declaration is necessary

    attribute = await _get_attribute(db, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if not attribute.can_edit(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    attribute.event.attribute_count -= 1
    if hard:
        await db.delete(attribute)
        await db.flush()
    else:
        attribute.deleted = True

    return DeleteAttributeResponse(message="Attribute deleted.")


@alog
async def _get_attributes(db: Session, user: User | None) -> list[GetAllAttributesResponse]:
    result = await db.execute(select(Attribute).filter(Attribute.can_access(user)))
    attributes = result.scalars().all()

    if not attributes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attributes found.")

    attribute_responses = [_prepare_attribute_response_get_all(attribute) for attribute in attributes]

    return attribute_responses


@alog
async def _rest_search_attributes(
    db: Session, body: SearchAttributesBody, user: User | None
) -> SearchAttributesResponse:
    if body.returnFormat != "json":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid output format.")

    filter = get_search_filters(**body.model_dump())
    qry = (
        select(Attribute)
        .filter(filter)
        .filter(Attribute.can_access(user))
        .options(
            selectinload(Attribute.local_tags),
            selectinload(Attribute.nonlocal_tags),
            selectinload(Attribute.mispobject),
        )
    )

    if body.limit is not None:
        body.page = body.page or 1
        qry = qry.limit(body.limit)
        qry = qry.offset((body.page - 1) * body.limit)

    result = await db.execute(qry)
    attributes: Sequence[Attribute] = result.scalars().all()

    response_list = []
    for attribute in attributes:
        attribute_dict = attribute.asdict()
        if attribute.event_id is not None:
            event_dict = attribute.event.asdict()
            event_dict["date"] = str(event_dict["date"])
            attribute_dict["Event"] = SearchAttributesEvent(**event_dict)
        if attribute.object_id != 0 and attribute.object_id is not None:
            object_dict = attribute.mispobject.__dict__.copy()
            attribute_dict["Object"] = SearchAttributesObject(**object_dict)

        if attribute.nonlocal_tags or attribute.local_tags:
            attribute_dict["Tag"] = []
            for tag in attribute.nonlocal_tags:
                tag_dict = tag.__dict__.copy()
                tag_dict["local"] = False
                attribute_dict["Tag"].append(GetAttributeTag(**tag_dict))
            for tag in attribute.local_tags:
                if not tag.exportable:
                    continue
                tag_dict = tag.__dict__.copy()
                tag_dict["local"] = True
                attribute_dict["Tag"].append(GetAttributeTag(**tag_dict))

        response_list.append(attribute_dict)
    return SearchAttributesResponse.model_validate({"response": {"Attribute": response_list}})


@alog
async def _restore_attribute(db: Session, attribute_id: int | uuid.UUID, user: User | None) -> GetAttributeResponse:
    attribute = await _get_attribute(db, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if not attribute.can_edit(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    setattr(attribute, "deleted", False)

    await db.flush()
    await db.refresh(attribute)

    await execute_workflow("attribute-after-save", db, attribute)

    attribute_data = await _prepare_get_attribute_details_response(db, attribute.id, attribute)

    return GetAttributeResponse(Attribute=attribute_data)


@alog
async def _add_tag_to_attribute(
    db: Session, attribute_id: int | uuid.UUID, tag_id: str, local: str, user: User | None
) -> AddRemoveTagAttributeResponse:
    attribute = await _get_attribute(db, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if not attribute.can_edit(user):
        logger.debug("User cannot edit %s", attribute.uuid)
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    try:
        int(tag_id)
    except ValueError:
        return AddRemoveTagAttributeResponse(saved=False, errors="Invalid Tag")

    tag = await db.get(Tag, tag_id)

    if not tag:
        return AddRemoveTagAttributeResponse(saved=False, errors="Tag could not be added.")

    if int(local) not in [0, 1]:
        return AddRemoveTagAttributeResponse(saved=False, errors="Invalid 'local'")
    local_output = local != "0"

    new_attribute_tag = AttributeTag(
        attribute_id=attribute.id, event_id=attribute.event_id, tag_id=tag.id, local=local_output
    )

    db.add(new_attribute_tag)

    await db.flush()
    await db.refresh(new_attribute_tag)

    return AddRemoveTagAttributeResponse(saved=True, success="Tag added", check_publish=True)


@alog
async def _remove_tag_from_attribute(
    db: Session, attribute_id: int | uuid.UUID, tag_id: str, user: User | None
) -> AddRemoveTagAttributeResponse:
    attribute = await _get_attribute(db, attribute_id)
    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if not attribute.can_edit(user):
        logger.debug("User cannot edit %s", attribute.id)
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail={"errors": "You do not have permission to do that.", "saved": False}
        )

    result = await db.execute(
        select(AttributeTag)
        .filter(AttributeTag.attribute_id == int(attribute.id), AttributeTag.tag_id == int(tag_id))
        .limit(1)
    )
    attribute_tag = result.scalars().one_or_none()

    if not attribute_tag:
        return AddRemoveTagAttributeResponse(saved=False, errors="Invalid attribute - tag combination.")

    await db.delete(attribute_tag)
    await db.flush()

    check_publish = not bool(attribute_tag.local)
    return AddRemoveTagAttributeResponse(saved=True, success="Tag removed.", check_publish=check_publish)


@log
def _prepare_attribute_response_add(attribute: Attribute) -> AddAttributeAttributes:
    attribute_dict = attribute.asdict()

    fields_to_convert = ["object_id", "sharing_group_id"]
    for field in fields_to_convert:
        attribute_dict[field] = str(attribute_dict.get(field, "0"))

    return AddAttributeAttributes(**attribute_dict)


@log
def _prepare_attribute_response_get_all(attribute: Attribute) -> GetAllAttributesResponse:
    attribute_dict = attribute.asdict()

    fields_to_convert = ["object_id", "sharing_group_id"]
    for field in fields_to_convert:
        attribute_dict[field] = str(attribute_dict.get(field, "0"))

    return GetAllAttributesResponse(**attribute_dict)


@alog
async def _prepare_get_attribute_details_response(
    db: Session, attribute_id: int | uuid.UUID, attribute: Attribute
) -> GetAttributeAttributes:
    attribute_dict = attribute.asdict()

    if "event_uuid" not in attribute_dict.keys():
        attribute_dict["event_uuid"] = attribute.event_uuid

    result = await db.execute(select(AttributeTag).filter(AttributeTag.attribute_id == attribute.id))
    db_attribute_tags = result.scalars().all()

    attribute_dict["Tag"] = []

    if db_attribute_tags is not None:
        for attribute_tag in db_attribute_tags:
            result2 = await db.execute(select(Tag).filter(Tag.id == attribute_tag.tag_id).limit(1))
            tag = result2.scalars().one_or_none()

            if not tag:
                raise HTTPException(status.HTTP_404_NOT_FOUND)

            connected_tag = GetAttributeTag(
                id=tag.id,
                name=tag.name,
                colour=tag.colour,
                numerical_value=tag.numerical_value,
                is_galaxy=tag.is_galaxy,
                local=attribute_tag.local,
            )
            attribute_dict["Tag"].append(connected_tag)

    return GetAttributeAttributes(**attribute_dict)


@alog
async def _prepare_edit_attribute_response(
    db: Session, attribute_id: int | uuid.UUID, attribute: Attribute
) -> EditAttributeAttributes:
    attribute_dict = attribute.asdict()

    fields_to_convert = ["object_id", "sharing_group_id", "timestamp"]
    for field in fields_to_convert:
        if attribute_dict.get(field) is not None:
            attribute_dict[field] = str(attribute_dict[field])
        else:
            attribute_dict[field] = "0"

    result = await db.execute(select(AttributeTag).filter(AttributeTag.attribute_id == attribute.id))
    db_attribute_tags = result.scalars().all()

    attribute_dict["Tag"] = []

    if db_attribute_tags is not None:
        for attribute_tag in db_attribute_tags:
            result = await db.execute(select(Tag).filter(Tag.id == attribute_tag.tag_id).limit(1))
            tag = result.scalars().one_or_none()

            if not tag:
                raise HTTPException(status.HTTP_404_NOT_FOUND)

            connected_tag = GetAttributeTag(
                id=tag.id,
                name=tag.name,
                colour=tag.colour,
                exportable=tag.exportable,
                user_id=tag.user_id,
                hide_tag=tag.hide_tag,
                numerical_value=tag.numerical_value,
                is_galaxy=tag.is_galaxy,
                is_costum_galaxy=tag.is_custom_galaxy,
                local=tag.local_only,
            )
            attribute_dict["Tag"].append(connected_tag)

    return EditAttributeAttributes(**attribute_dict)


@alog
async def _get_attribute_category_statistics(db: Session, percentage: bool) -> GetAttributeStatisticsCategoriesResponse:  # type: ignore
    qry = select(Attribute.category, func.count(Attribute.category).label("count")).group_by(Attribute.category)
    result = await db.execute(qry)
    attribute_count_by_category = result.all()

    attribute_count_by_category_dict: dict[str, int] = {
        x.category: cast(int, x.count) for x in attribute_count_by_category
    }

    if percentage:
        total_count_of_attributes = sum(cast(int, x.count) for x in attribute_count_by_category)
        percentages = {
            k: f"{str(round(v / total_count_of_attributes * 100, 3)).rstrip('0').rstrip('.')}%"
            for k, v in attribute_count_by_category_dict.items()
        }
        return GetAttributeStatisticsCategoriesResponse(**percentages)

    return GetAttributeStatisticsCategoriesResponse(**attribute_count_by_category_dict)


@alog
async def _get_attribute_type_statistics(
    db: Session, percentage: bool, user: User | None
) -> GetAttributeStatisticsTypesResponse:  # type: ignore
    qry = select(Attribute.type, func.count(Attribute.type).label("count")).group_by(Attribute.type)
    result = await db.execute(qry)
    attribute_count_by_group = result.all()
    attribute_count_by_group_dict: dict[str, int] = {x.type: cast(int, x.count) for x in attribute_count_by_group}

    if percentage:
        total_count_of_attributes = sum(cast(int, x.count) for x in attribute_count_by_group)
        percentages = {
            k: f"{str(round(v / total_count_of_attributes * 100, 3)).rstrip('0').rstrip('.')}%"
            for k, v in attribute_count_by_group_dict.items()
        }
        return GetAttributeStatisticsTypesResponse(**percentages)

    return GetAttributeStatisticsTypesResponse(**attribute_count_by_group_dict)


async def _get_event_by_uuid(event_id: uuid.UUID, db: Session) -> Event | None:
    """Get's an event by its UUID.

    args:
        event_id: the UUID of the event
        db: the current db

    returns:
        The event with the associated UUID of NONE in case of not being present.

    """
    query: Select = select(Event).filter(Event.uuid == event_id)

    result = await db.execute(query)
    event = result.scalars().one_or_none()

    return event


async def _get_attribute(
    db: Session, attribute_id: int | uuid.UUID, load_sharing_group: bool = False
) -> Attribute | None:
    """Get's an attribute by its ID or UUID.

    args:
        db: the current db
        attribute_id: the uuid of the attribute to get

    returns:
        The attribute with the associated UUID of NONE in case of not being present.

    """
    query = select(Attribute)
    if isinstance(attribute_id, int):
        query = query.filter(Attribute.id == attribute_id)
    else:
        query = query.filter(Attribute.uuid == attribute_id)

    if load_sharing_group:
        query = query.options(selectinload(Attribute.sharing_group))

    result = await db.execute(query)
    attribute = result.scalars().one_or_none()

    return attribute


async def _get_tag_by_attribute_uuid(db: Session, attribute_id: uuid.UUID, tag_id: int) -> AttributeTag | None:
    """Get's an attributes tag by the attributes UUID and the tags ID.

    args:
        db: the current db
        attribute_id: the UUID of the attribute
        tag_id: the ID of the tag

    returns:
        The tag of the attribute with the associated UUID an ID or None in case of not being present.

    """
    query: Select = (
        select(AttributeTag).filter(AttributeTag.attribute_uuid == attribute_id, AttributeTag.tag_id == tag_id).limit(1)
    )

    result = await db.execute(query)
    attribute_tag = result.scalars().one_or_none()

    return attribute_tag
