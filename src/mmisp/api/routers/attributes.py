from collections.abc import Sequence
from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.attributes import (
    AddAttributeAttributes,
    AddAttributeBody,
    AddAttributeResponse,
    AddRemoveTagAttributeResponse,
    DeleteAttributeResponse,
    DeleteSelectedAttributeBody,
    DeleteSelectedAttributeResponse,
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
from mmisp.lib.attribute_search_filter import get_search_filters
from mmisp.lib.logger import alog, log
from mmisp.util.models import update_record

from ..workflow import execute_workflow

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

    Input:

    - the user's authentification status

    - the current database

    - the search body

    Output:

    - the attributes the search finds
    """
    return await _rest_search_attributes(db, body)


@router.post(
    "/attributes/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=AddAttributeResponse,
    summary="Add new attribute",
)
@alog
async def add_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(alias="eventId")],
    body: AddAttributeBody,
) -> AddAttributeResponse:
    """Add a new attribute with the given details.

    Input:

    - the user's authentification status

    - the current database

    - the id of the event

    - the body for adding an attribute

    Output:

    - the response of the added attribute from the api
    """
    return await _add_attribute(db, event_id, body)


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

    Input:

    - the user's authentification status

    Output:

    - the attributes describe types
    """
    return GetDescribeTypesResponse(result=GetDescribeTypesAttributes())


@router.get(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=GetAttributeResponse,
    summary="Get attribute details",
)
@alog
async def get_attribute_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[int, Path(alias="attributeId")],
) -> GetAttributeResponse:
    """Retrieve details of a specific attribute by its ID.

    Input:

    - the user's authentification status

    - the current database

    - the id of the attribute

    Output:

    - the attribute details
    """
    return await _get_attribute_details(db, attribute_id)


@router.put(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=EditAttributeResponse,
    summary="Update an attribute",
)
@alog
async def update_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
    body: EditAttributeBody,
) -> EditAttributeResponse:
    """Update an existing attribute by its ID.

    Input:

    - the user's authentification status

    - the current database

    - the id of the attribute

    - the body for editing the attribute

    Output:

    - the response from the api for the edit request
    """
    return await _update_attribute(db, attribute_id, body)


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
    attribute_id: Annotated[str, Path(alias="attributeId")],
) -> DeleteAttributeResponse:
    """Delete an attribute by its ID.

    Input:

    - the user's authentification status

    - the current database

    - the id of the attribute

    Output:

    - the response from the api for the delete request
    """
    return await _delete_attribute(db, attribute_id)


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

    Input:

    - the user's authentification status

    Output:

    - the list of all attributes
    """
    return await _get_attributes(db)


@router.post(
    "/attributes/deleteSelected/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteSelectedAttributeResponse,
    summary="Delete the selected attributes",
)
@alog
async def delete_selected_attributes(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(alias="eventId")],
    body: DeleteSelectedAttributeBody,
    request: Request,
) -> DeleteSelectedAttributeResponse:
    """Deletes the attributes associated with the event from the list in the body.

    Input:

    - the user's authentification status

    - the current database

    - the id of the event

    - the body for deleting the selected attributes

    - the request

    Output:

    - the response from the api for the deleting of the selection
    """
    return await _delete_selected_attributes(db, event_id, body, request)


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

    Input:

    - the user's authentification status
    - the current database
    - percentage

    Output:

    - the attributes statistics for one category/type
    """
    return await _get_attribute_type_statistics(db, percentage)


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

    Input:

    - the user's authentification status
    - the current database
    - percentage

    Output:

    - the attributes statistics for one category/type
    """
    return await _get_attribute_category_statistics(db, percentage)


@router.post(
    "/attributes/restore/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=GetAttributeResponse,
    summary="Restore an attribute",
)
@alog
async def restore_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
) -> GetAttributeResponse:
    """Restore an attribute by its ID.

    Input:

    - the user's authentification status

    - the current database

    - the id of the attribute

    Output:

    - the restored attribute
    """
    return await _restore_attribute(db, attribute_id)


@router.post(
    "/attributes/addTag/{attributeId}/{tagId}/local:{local}",
    status_code=status.HTTP_200_OK,
    response_model=AddRemoveTagAttributeResponse,
    summary="Add tag to attribute",
)
@alog
async def add_tag_to_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.TAGGER]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
    tag_id: Annotated[str, Path(alias="tagId")],
    local: str,
) -> AddRemoveTagAttributeResponse:
    """Add a tag to an attribute by there ids.

    Input:

    - the user's authentification status

    - the current database

    - the id of the attribute

    - the id of the tag

    - local

    Output:

    - the response from the api for adding a tag to an attribute
    """
    return await _add_tag_to_attribute(db, attribute_id, tag_id, local)


@router.post(
    "/attributes/removeTag/{attributeId}/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=AddRemoveTagAttributeResponse,
    summary="Remove tag from attribute",
)
@alog
async def remove_tag_from_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.TAGGER]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
    tag_id: Annotated[str, Path(alias="tagId")],
) -> AddRemoveTagAttributeResponse:
    """Remove a tag from an attribute by there ids.

    Input:

    - the user's authentification status

    - the current database

    - the id of the attribute

    - the id of the tag

    Output:

    - the response from the api for removing a tag to an attribute
    """
    return await _remove_tag_from_attribute(db, attribute_id, tag_id)


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
    event_id: Annotated[str, Path(alias="eventId")],
    body: AddAttributeBody,
) -> AddAttributeResponse:
    """Deprecated. Add a new attribute with the given details using the old route.

    Input:

    - the user's authentification status

    - the current database

    - the id of the event

    - the body

    Output:

    - the attribute
    """
    return await _add_attribute(db, event_id, body)


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

    Input:

    - the user's authentification status

    - the current database

    - the id of the attribute

    Output:

    - the details of an attribute
    """
    return await _get_attribute_details(db, attribute_id)


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
    attribute_id: Annotated[str, Path(alias="attributeId")],
    body: EditAttributeBody,
) -> EditAttributeResponse:
    """Deprecated. Update an existing attribute by its ID using the old route.

    Input:

    - the user's authentification status

    - the current database

    - the id of the attribute

    - the body

    Output:

    - the updated version af an attribute
    """
    return await _update_attribute(db, attribute_id, body)


@router.delete(
    "/attributes/delete/{attributeId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=DeleteAttributeResponse,
    summary="Delete an Attribute (Deprecated)",
)
@alog
async def delete_attribute_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
) -> DeleteAttributeResponse:
    """Deprecated. Delete an attribute by its ID using the old route.

    Input:

    - the user's authentification status

    - the current database

    - the id of the attribute

    Output:

    - the response from the api for the deleting request
    """
    return await _delete_attribute(db, attribute_id)


# --- endpoint logic ---


@alog
async def _add_attribute(db: Session, event_id: str, body: AddAttributeBody) -> AddAttributeResponse:
    event: Event | None = await db.get(Event, event_id)

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
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
            **body.dict(),
            "event_id": int(event_id),
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
async def _get_attribute_details(db: Session, attribute_id: int) -> GetAttributeResponse:
    attribute: Attribute | None = await db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    attribute_data = await _prepare_get_attribute_details_response(db, attribute_id, attribute)

    return GetAttributeResponse(Attribute=attribute_data)


@alog
async def _update_attribute(db: Session, attribute_id: str, body: EditAttributeBody) -> EditAttributeResponse:
    attribute: Attribute | None = await db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    # first_seen/last_seen being an empty string is accepted by legacy MISP
    # and implies "field is not set".
    payload = body.dict()
    for seen in ["first_seen", "last_seen"]:
        if seen in payload and not payload[seen]:
            payload[seen] = None

    update_record(attribute, payload)

    await execute_workflow("attribute-after-save", db, attribute)

    await db.flush()
    await db.refresh(attribute)

    attribute_data = await _prepare_edit_attribute_response(db, attribute_id, attribute)

    return EditAttributeResponse(Attribute=attribute_data)


@alog
async def _delete_attribute(db: Session, attribute_id: str) -> DeleteAttributeResponse:
    attribute: Attribute | None = await db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.delete(attribute)
    await db.flush()

    return DeleteAttributeResponse(message="Attribute deleted.")


@alog
async def _get_attributes(db: Session) -> list[GetAllAttributesResponse]:
    result = await db.execute(select(Attribute))
    attributes = result.scalars().all()

    if not attributes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attributes found.")

    attribute_responses = [_prepare_attribute_response_get_all(attribute) for attribute in attributes]

    return attribute_responses


@alog
async def _delete_selected_attributes(
    db: Session, event_id: str, body: DeleteSelectedAttributeBody, request: Request
) -> DeleteSelectedAttributeResponse:
    event: Event | None = await db.get(Event, event_id)

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    attribute_ids = body.id.split(" ")

    for attribute_id in attribute_ids:
        attribute: Attribute | None = await db.get(Attribute, attribute_id)

        if not attribute:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        if not attribute.event.id == int(event_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No attribute with id '{attribute_id}' found in the given event.",
            )

        if body.allow_hard_delete:
            await db.delete(attribute)
            await db.flush()
        else:
            setattr(attribute, "deleted", True)
            await db.flush()

            await db.refresh(attribute)

    attribute_count = len(attribute_ids)
    attribute_str = "attribute" if attribute_count == 1 else "attributes"

    return DeleteSelectedAttributeResponse(
        saved=True,
        success=True,
        name=f"{attribute_count} {attribute_str} deleted.",
        message=f"{attribute_count} {attribute_str} deleted.",
        url=str(request.url.path),
        id=str(event_id),
    )


@alog
async def _rest_search_attributes(db: Session, body: SearchAttributesBody) -> SearchAttributesResponse:
    if body.returnFormat != "json":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid output format.")

    filter = get_search_filters(**body.dict())
    qry = (
        select(Attribute)
        .filter(filter)
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
        attribute_dict = attribute.asdict().copy()
        if attribute.event_id is not None:
            event_dict = attribute.event.__dict__.copy()
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
    return SearchAttributesResponse.parse_obj({"response": {"Attribute": response_list}})


@alog
async def _restore_attribute(db: Session, attribute_id: str) -> GetAttributeResponse:
    attribute: Attribute | None = await db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    setattr(attribute, "deleted", False)

    await db.flush()
    await db.refresh(attribute)

    await execute_workflow("attribute-after-save", db, attribute)

    attribute_data = await _prepare_get_attribute_details_response(db, attribute.id, attribute)

    return GetAttributeResponse(Attribute=attribute_data)


@alog
async def _add_tag_to_attribute(
    db: Session, attribute_id: str, tag_id: str, local: str
) -> AddRemoveTagAttributeResponse:
    attribute: Attribute | None = await db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

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
async def _remove_tag_from_attribute(db: Session, attribute_id: str, tag_id: str) -> AddRemoveTagAttributeResponse:
    result = await db.execute(
        select(AttributeTag)
        .filter(AttributeTag.attribute_id == int(attribute_id), AttributeTag.tag_id == int(tag_id))
        .limit(1)
    )
    attribute_tag = result.scalars().first()

    if not attribute_tag:
        return AddRemoveTagAttributeResponse(saved=False, errors="Invalid attribute - tag combination.")

    await db.delete(attribute_tag)
    await db.flush()

    return AddRemoveTagAttributeResponse(saved=True, success="Tag removed", check_publish=True)


@log
def _prepare_attribute_response_add(attribute: Attribute) -> AddAttributeAttributes:
    attribute_dict = attribute.asdict().copy()

    fields_to_convert = ["object_id", "sharing_group_id"]
    for field in fields_to_convert:
        attribute_dict[field] = str(attribute_dict.get(field, "0"))

    return AddAttributeAttributes(**attribute_dict)


@log
def _prepare_attribute_response_get_all(attribute: Attribute) -> GetAllAttributesResponse:
    attribute_dict = attribute.asdict().copy()

    fields_to_convert = ["object_id", "sharing_group_id"]
    for field in fields_to_convert:
        attribute_dict[field] = str(attribute_dict.get(field, "0"))

    return GetAllAttributesResponse(**attribute_dict)


@alog
async def _prepare_get_attribute_details_response(
    db: Session, attribute_id: int, attribute: Attribute
) -> GetAttributeAttributes:
    attribute_dict = attribute.asdict().copy()
    if "event_uuid" not in attribute_dict.keys():
        attribute_dict["event_uuid"] = attribute.event_uuid

    result = await db.execute(select(AttributeTag).filter(AttributeTag.attribute_id == attribute_id))
    db_attribute_tags = result.scalars().all()

    attribute_dict["Tag"] = []

    if len(db_attribute_tags) > 0:
        for attribute_tag in db_attribute_tags:
            result = await db.execute(select(Tag).filter(Tag.id == attribute_tag.tag_id).limit(1))
            tag = result.scalars().one()

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
    db: Session, attribute_id: str, attribute: Attribute
) -> EditAttributeAttributes:
    attribute_dict = attribute.asdict().copy()

    fields_to_convert = ["object_id", "sharing_group_id", "timestamp"]
    for field in fields_to_convert:
        if attribute_dict.get(field) is not None:
            attribute_dict[field] = str(attribute_dict[field])
        else:
            attribute_dict[field] = "0"

    result = await db.execute(select(AttributeTag).filter(AttributeTag.attribute_id == attribute_id))
    db_attribute_tags = result.scalars().all()
    attribute_dict["Tag"] = []

    if len(db_attribute_tags) > 0:
        for attribute_tag in db_attribute_tags:
            result = await db.execute(select(Tag).filter(Tag.id == attribute_tag.tag_id).limit(1))
            tag = result.scalars().one()
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
            k: f"{str(round(v / total_count_of_attributes * 100, 3)).rstrip('.0')}%"
            for k, v in attribute_count_by_category_dict.items()
        }
        return GetAttributeStatisticsCategoriesResponse(**percentages)

    return GetAttributeStatisticsCategoriesResponse(**attribute_count_by_category_dict)


@alog
async def _get_attribute_type_statistics(db: Session, percentage: bool) -> GetAttributeStatisticsTypesResponse:  # type: ignore
    qry = select(Attribute.type, func.count(Attribute.type).label("count")).group_by(Attribute.type)
    result = await db.execute(qry)
    attribute_count_by_group = result.all()
    attribute_count_by_group_dict: dict[str, int] = {x.type: cast(int, x.count) for x in attribute_count_by_group}

    if percentage:
        total_count_of_attributes = sum(cast(int, x.count) for x in attribute_count_by_group)
        percentages = {
            k: f"{str(round(v / total_count_of_attributes * 100, 3)).strip('.0')}%"
            for k, v in attribute_count_by_group_dict.items()
        }
        return GetAttributeStatisticsTypesResponse(**percentages)

    return GetAttributeStatisticsTypesResponse(**attribute_count_by_group_dict)
