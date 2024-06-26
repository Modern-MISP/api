import typing
from collections.abc import Sequence
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from sqlalchemy import func, select

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
from mmisp.db.models.object import Object
from mmisp.db.models.tag import Tag
from mmisp.util.models import update_record

router = APIRouter(tags=["attributes"])


@router.post(
    "/attributes/restSearch",
    status_code=status.HTTP_200_OK,
    summary="Search attributes",
    description="Search for attributes based on various filters.",
)
async def rest_search_attributes(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: SearchAttributesBody,
) -> SearchAttributesResponse:
    return await _rest_search_attributes(db, body)


@router.post(
    "/attributes/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=AddAttributeResponse,
    summary="Add new attribute",
    description="Add a new attribute with the given details.",
)
async def add_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(alias="eventId")],
    body: AddAttributeBody,
) -> AddAttributeResponse:
    return await _add_attribute(db, event_id, body)


@router.get(
    "/attributes/describeTypes",
    status_code=status.HTTP_200_OK,
    response_model=GetDescribeTypesResponse,
    summary="Get all attribute describe types",
    description="Retrieve a list of all available attribute types and categories.",
)
async def get_attributes_describe_types(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
) -> GetDescribeTypesResponse:
    return GetDescribeTypesResponse(result=GetDescribeTypesAttributes())


@router.get(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=GetAttributeResponse,
    summary="Get attribute details",
    description="Retrieve details of a specific attribute by its ID.",
)
async def get_attribute_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
) -> GetAttributeResponse:
    return await _get_attribute_details(db, attribute_id)


@router.put(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=EditAttributeResponse,
    summary="Update an attribute",
    description="Update an existing attribute by its ID.",
)
async def update_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
    body: EditAttributeBody,
) -> EditAttributeResponse:
    return await _update_attribute(db, attribute_id, body)


@router.delete(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteAttributeResponse,
    summary="Delete an Attribute",
    description="Delete an attribute by its ID.",
)
async def delete_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
) -> DeleteAttributeResponse:
    return await _delete_attribute(db, attribute_id)


@router.get(
    "/attributes",
    status_code=status.HTTP_200_OK,
    summary="Get all Attributes",
    description="Retrieve a list of all attributes.",
)
async def get_attributes(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> list[GetAllAttributesResponse]:
    return await _get_attributes(db)


@router.post(
    "/attributes/deleteSelected/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteSelectedAttributeResponse,
    summary="Delete the selected attributes",
    description="Deletes the attributes associated with the event from the list in the body.",
)
async def delete_selected_attributes(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(alias="eventId")],
    body: DeleteSelectedAttributeBody,
    request: Request,
) -> DeleteSelectedAttributeResponse:
    return await _delete_selected_attributes(db, event_id, body, request)


@router.get(
    "/attributes/attributeStatistics/{context}/{percentage}",
    status_code=status.HTTP_200_OK,
    summary="Get attribute statistics",
    description="Get the count/percentage of attributes per category/type.",
)
async def get_attributes_statistics(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    context: Literal["type"] | Literal["category"],
    percentage: bool,
) -> GetAttributeStatisticsCategoriesResponse | GetAttributeStatisticsTypesResponse:  # type: ignore
    return await _get_attribute_statistics(db, context, percentage)


@router.post(
    "/attributes/restore/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=GetAttributeResponse,
    summary="Restore an attribute",
    description="Restore an attribute by its ID.",
)
async def restore_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
) -> GetAttributeResponse:
    return await _restore_attribute(db, attribute_id)


@router.post(
    "/attributes/addTag/{attributeId}/{tagId}/local:{local}",
    status_code=status.HTTP_200_OK,
    response_model=AddRemoveTagAttributeResponse,
    summary="Add tag to attribute",
    description="Add a tag to an attribute by there ids.",
)
async def add_tag_to_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.TAGGER]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
    tag_id: Annotated[str, Path(alias="tagId")],
    local: str,
) -> AddRemoveTagAttributeResponse:
    return await _add_tag_to_attribute(db, attribute_id, tag_id, local)


@router.post(
    "/attributes/removeTag/{attributeId}/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=AddRemoveTagAttributeResponse,
    summary="Remove tag from attribute",
    description="Remove a tag from an attribute by there ids.",
)
async def remove_tag_from_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.TAGGER]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
    tag_id: Annotated[str, Path(alias="tagId")],
) -> AddRemoveTagAttributeResponse:
    return await _remove_tag_from_attribute(db, attribute_id, tag_id)


# --- deprecated ---


@router.post(
    "/attributes/add/{eventId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=AddAttributeResponse,
    summary="Add new attribute (Deprecated)",
    description="Deprecated. Add a new attribute with the given details using the old route.",
)
async def add_attribute_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(alias="eventId")],
    body: AddAttributeBody,
) -> AddAttributeResponse:
    return await _add_attribute(db, event_id, body)


@router.get(
    "/attributes/view/{attributeId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=GetAttributeResponse,
    summary="Get attribute details (Deprecated)",
    description="Deprecated. Retrieve details of a specific attribute by its ID using the old route.",
)
async def get_attribute_details_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
) -> GetAttributeResponse:
    return await _get_attribute_details(db, attribute_id)


@router.put(
    "/attributes/edit/{attributeId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=EditAttributeResponse,
    summary="Update an attribute (Deprecated)",
    description="Deprecated. Update an existing attribute by its ID using the old route.",
)
async def update_attribute_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
    body: EditAttributeBody,
) -> EditAttributeResponse:
    return await _update_attribute(db, attribute_id, body)


@router.delete(
    "/attributes/delete/{attributeId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=DeleteAttributeResponse,
    summary="Delete an Attribute (Deprecated)",
    description="Deprecated. Delete an attribute by its ID using the old route.",
)
async def delete_attribute_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(alias="attributeId")],
) -> DeleteAttributeResponse:
    return await _delete_attribute(db, attribute_id)


# --- endpoint logic ---


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
    await db.commit()

    await db.refresh(new_attribute)
    setattr(event, "attribute_count", event.attribute_count + 1)

    attribute_data = _prepare_attribute_response_add(new_attribute)

    return AddAttributeResponse(Attribute=attribute_data)


async def _get_attribute_details(db: Session, attribute_id: str) -> GetAttributeResponse:
    attribute: Attribute | None = await db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    attribute_data = await _prepare_get_attribute_details_response(db, attribute_id, attribute)

    return GetAttributeResponse(Attribute=attribute_data)


async def _update_attribute(db: Session, attribute_id: str, body: EditAttributeBody) -> EditAttributeResponse:
    attribute: Attribute | None = await db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    update_record(attribute, body.dict())

    await db.commit()
    await db.refresh(attribute)

    attribute_data = await _prepare_edit_attribute_response(db, attribute_id, attribute)

    return EditAttributeResponse(Attribute=attribute_data)


async def _delete_attribute(db: Session, attribute_id: str) -> DeleteAttributeResponse:
    attribute: Attribute | None = await db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.delete(attribute)
    await db.commit()

    return DeleteAttributeResponse(message="Attribute deleted.")


async def _get_attributes(db: Session) -> list[GetAllAttributesResponse]:
    result = await db.execute(select(Attribute))
    attributes = result.scalars().all()

    if not attributes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attributes found.")

    attribute_responses = [_prepare_attribute_response_get_all(attribute) for attribute in attributes]

    return attribute_responses


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
            await db.commit()
        else:
            setattr(attribute, "deleted", True)
            await db.commit()

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


async def _rest_search_attributes(db: Session, body: SearchAttributesBody) -> SearchAttributesResponse:
    if body.returnFormat != "json":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid output format.")

    result = await db.execute(select(Attribute))
    attributes: Sequence[Attribute] = result.scalars().all()
    if body.limit is not None:
        attributes = attributes[: body.limit]
    response_list = []
    for attribute in attributes:
        attribute_dict = attribute.asdict().copy()
        if attribute.event_id is not None:
            event = await db.get(Event, attribute.event_id)
            event_dict = event.__dict__.copy()
            event_dict["date"] = str(event_dict["date"])
            attribute_dict["Event"] = SearchAttributesEvent(**event_dict)
        if attribute.object_id != 0:
            object = await db.get(Object, attribute.object_id)
            object_dict = object.__dict__.copy()
            attribute_dict["Object"] = SearchAttributesObject(**object_dict)

        result = await db.execute(select(AttributeTag).filter(AttributeTag.attribute_id == attribute.id))
        attribute_tags = result.scalars().all()
        attribute_dict["Tag"] = []
        for attribute_tag in attribute_tags:
            tag = await db.get(Tag, attribute_tag.tag_id)
            tag_dict = tag.__dict__.copy()
            tag_dict["local"] = attribute_tag.local
            attribute_dict["Tag"].append(GetAttributeTag(**tag_dict))

        response_list.append(attribute_dict)
    return SearchAttributesResponse.parse_obj({"response": {"Attribute": response_list}})


async def _get_attribute_statistics(
    db: Session, context: Literal["type"] | Literal["category"], percentage: bool
) -> GetAttributeStatisticsTypesResponse | GetAttributeStatisticsCategoriesResponse:  # type: ignore
    result = await db.execute(select(func.count()).select_from(Attribute))
    total_count_of_attributes = typing.cast(int, result.scalar())

    if context == "category":
        return await _category_statistics(db, percentage, total_count_of_attributes)
    else:
        return await _type_statistics(db, percentage, total_count_of_attributes)


async def _restore_attribute(db: Session, attribute_id: str) -> GetAttributeResponse:
    attribute: Attribute | None = await db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    setattr(attribute, "deleted", False)

    await db.commit()
    await db.refresh(attribute)

    attribute_data = await _prepare_get_attribute_details_response(db, str(attribute.id), attribute)

    return GetAttributeResponse(Attribute=attribute_data)


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

    await db.commit()
    await db.refresh(new_attribute_tag)

    return AddRemoveTagAttributeResponse(saved=True, success="Tag added", check_publish=True)


async def _remove_tag_from_attribute(db: Session, attribute_id: str, tag_id: str) -> AddRemoveTagAttributeResponse:
    attribute: Attribute | None = await db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    try:
        int(tag_id)
    except ValueError:
        return AddRemoveTagAttributeResponse(saved=False, errors="Invalid Tag")
    if not await db.get(Tag, tag_id):
        return AddRemoveTagAttributeResponse(saved=False, errors="Tag could not be removed.")

    result = await db.execute(select(AttributeTag).filter(AttributeTag.attribute_id == attribute_id).limit(1))
    attribute_tag = result.scalars().first()

    if not attribute_tag:
        return AddRemoveTagAttributeResponse(saved=False, errors="Invalid attribute - tag combination.")

    await db.delete(attribute_tag)
    await db.commit()

    return AddRemoveTagAttributeResponse(saved=True, success="Tag removed", check_publish=True)


def _prepare_attribute_response_add(attribute: Attribute) -> AddAttributeAttributes:
    attribute_dict = attribute.asdict().copy()

    fields_to_convert = ["object_id", "sharing_group_id"]
    for field in fields_to_convert:
        attribute_dict[field] = str(attribute_dict.get(field, "0"))

    return AddAttributeAttributes(**attribute_dict)


def _prepare_attribute_response_get_all(attribute: Attribute) -> GetAllAttributesResponse:
    attribute_dict = attribute.asdict().copy()

    fields_to_convert = ["object_id", "sharing_group_id"]
    for field in fields_to_convert:
        attribute_dict[field] = str(attribute_dict.get(field, "0"))

    return GetAllAttributesResponse(**attribute_dict)


async def _prepare_get_attribute_details_response(
    db: Session, attribute_id: str, attribute: Attribute
) -> GetAttributeAttributes:
    attribute_dict = attribute.asdict().copy()
    if "event_uuid" not in attribute_dict.keys():
        attribute_dict["event_uuid"] = attribute.event_uuid

    fields_to_convert = ["object_id", "sharing_group_id", "timestamp"]

    for field in fields_to_convert:
        if attribute_dict.get(field) is not None:
            attribute_dict[field] = str(attribute_dict[field])
        else:
            attribute_dict[field] = "0"

    result = await db.execute(select(AttributeTag).filter(AttributeTag.attribute_id == attribute_id))
    db_attribute_tags = result.scalars().all()

    attribute_dict["tag"] = []

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
            attribute_dict["tag"].append(connected_tag)

    return GetAttributeAttributes(**attribute_dict)


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
    attribute_dict["tag"] = []

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
            attribute_dict["tag"].append(connected_tag)

    return EditAttributeAttributes(**attribute_dict)


async def _category_statistics(
    db: Session, percentage: int, total_count_of_attributes: int
) -> GetAttributeStatisticsCategoriesResponse:
    response_dict = {}

    if total_count_of_attributes == 0:
        return GetAttributeStatisticsCategoriesResponse(**{x: "" for x in GetDescribeTypesAttributes().categories})

    for category in GetDescribeTypesAttributes().categories:
        if percentage == 1:
            response_dict[category] = (
                str(
                    round(
                        (await _count_of_attributes_with_given_category(db, category) / total_count_of_attributes)
                        * 100,
                        2,
                    )
                )
                + "%"
            )
        else:
            response_dict[category] = str(await _count_of_attributes_with_given_category(db, category))

    return GetAttributeStatisticsCategoriesResponse(**response_dict)


async def _type_statistics(
    db: Session, percentage: int, total_count_of_attributes: int
) -> GetAttributeStatisticsTypesResponse:  # type: ignore
    response_dict = {}

    if total_count_of_attributes == 0:
        return GetAttributeStatisticsTypesResponse(**{x: "" for x in GetDescribeTypesAttributes().types})

    for type in GetDescribeTypesAttributes().types:
        if percentage == 1:
            response_dict[type] = (
                str(round((await _count_of_attributes_with_given_type(db, type) / total_count_of_attributes) * 100, 2))
                + "%"
            )
        else:
            response_dict[type] = str(await _count_of_attributes_with_given_type(db, type))

    return GetAttributeStatisticsTypesResponse(**response_dict)


# todo: use count function instead of len()
async def _count_of_attributes_with_given_category(db: Session, category: str) -> int:
    result = await db.execute(select(Attribute).filter(Attribute.category == category))
    attributes_with_given_category = result.scalars().all()
    return len(attributes_with_given_category)


# todo: use count function instead of len()
async def _count_of_attributes_with_given_type(db: Session, type: str) -> int:
    result = await db.execute(select(Attribute).filter(Attribute.type == type))
    attributes_with_given_type = result.scalars().all()
    return len(attributes_with_given_type)
