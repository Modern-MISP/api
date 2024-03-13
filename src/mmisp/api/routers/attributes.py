from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.attributes.add_attribute_body import AddAttributeBody
from mmisp.api_schemas.attributes.add_attribute_response import AddAttributeAttributes, AddAttributeResponse
from mmisp.api_schemas.attributes.add_remove_tag_attribute_response import AddRemoveTagAttributeResponse
from mmisp.api_schemas.attributes.delete_attribute_response import DeleteAttributeResponse
from mmisp.api_schemas.attributes.delete_selected_attribute_body import DeleteSelectedAttributeBody
from mmisp.api_schemas.attributes.delete_selected_attribute_response import DeleteSelectedAttributeResponse
from mmisp.api_schemas.attributes.edit_attribute_body import EditAttributeBody
from mmisp.api_schemas.attributes.edit_attributes_response import EditAttributeAttributes, EditAttributeResponse
from mmisp.api_schemas.attributes.get_all_attributes_response import GetAllAttributesResponse
from mmisp.api_schemas.attributes.get_attribute_response import (
    GetAttributeAttributes,
    GetAttributeResponse,
    GetAttributeTag,
)
from mmisp.api_schemas.attributes.get_attribute_statistics_response import (
    GetAttributeStatisticsCategoriesResponse,
    GetAttributeStatisticsTypesResponse,
)
from mmisp.api_schemas.attributes.get_describe_types_response import (
    GetDescribeTypesAttributes,
    GetDescribeTypesResponse,
)
from mmisp.api_schemas.attributes.search_attributes_body import SearchAttributesBody
from mmisp.api_schemas.attributes.search_attributes_response import (
    SearchAttributesAttributes,
    SearchAttributesAttributesDetails,
    SearchAttributesEvent,
    SearchAttributesObject,
    SearchAttributesResponse,
)
from mmisp.db.database import get_db, with_session_management
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.event import Event
from mmisp.db.models.object import Object
from mmisp.db.models.tag import Tag
from mmisp.util.models import update_record
from mmisp.util.partial import partial

router = APIRouter(tags=["attributes"])


@router.post(
    "/attributes/restSearch",
    status_code=status.HTTP_200_OK,
    response_model=partial(SearchAttributesResponse),
    summary="Search attributes",
    description="Search for attributes based on various filters.",
)
@with_session_management
async def rest_search_attributes(db: Annotated[Session, Depends(get_db)], body: SearchAttributesBody) -> dict:
    return await _rest_search_attributes(db, body)


@router.post(
    "/attributes/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(AddAttributeResponse),
    summary="Add new attribute",
    description="Add a new attribute with the given details.",
)
@with_session_management
async def add_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    body: AddAttributeBody,
) -> dict:
    return await _add_attribute(db, event_id, body)


@router.get(
    "/attributes/describeTypes",
    status_code=status.HTTP_200_OK,
    response_model=partial(GetDescribeTypesResponse),
    summary="Get all attribute describe types",
    description="Retrieve a list of all available attribute types and categories.",
)
async def get_attributes_describe_types() -> GetDescribeTypesResponse:
    return GetDescribeTypesResponse(result=GetDescribeTypesAttributes())


@router.get(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(GetAttributeResponse),
    summary="Get attribute details",
    description="Retrieve details of a specific attribute by its ID.",
)
@with_session_management
async def get_attribute_details(
    db: Annotated[Session, Depends(get_db)], attribute_id: Annotated[str, Path(..., alias="attributeId")]
) -> dict:
    return await _get_attribute_details(db, attribute_id)


@router.put(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(EditAttributeResponse),
    summary="Update an attribute",
    description="Update an existing attribute by its ID.",
)
@with_session_management
async def update_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(..., alias="attributeId")],
    body: EditAttributeBody,
) -> dict:
    return await _update_attribute(db, attribute_id, body)


@router.delete(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteAttributeResponse,
    summary="Delete an Attribute",
    description="Delete an attribute by its ID.",
)
@with_session_management
async def delete_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(..., alias="attributeId")],
) -> dict:
    return await _delete_attribute(db, attribute_id)


@router.get(
    "/attributes",
    status_code=status.HTTP_200_OK,
    response_model=list[GetAllAttributesResponse],
    summary="Get all Attributes",
    description="Retrieve a list of all attributes.",
)
@with_session_management
async def get_attributes(db: Annotated[Session, Depends(get_db)]) -> list[dict]:
    return await _get_attributes(db)


@router.post(
    "/attributes/deleteSelected/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(DeleteSelectedAttributeResponse),
    summary="Delete the selected attributes",
)
@with_session_management
async def delete_selected_attributes(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    body: DeleteSelectedAttributeBody,
    request: Request,
) -> dict:
    return await _delete_selected_attributes(db, event_id, body, request)


@router.get(
    "/attributes/attributeStatistics/{context}/{percentage}",
    status_code=status.HTTP_200_OK,
    response_model=GetAttributeStatisticsCategoriesResponse,
    summary="Get attribute statistics",
    description="Get the count/percentage of attributes per category/type.",
)
@with_session_management
async def get_attributes_statistics(
    db: Annotated[Session, Depends(get_db)], context: str, percentage: int
) -> GetAttributeStatisticsCategoriesResponse:
    return await _get_attribute_statistics(db, context, percentage)


@router.post(
    "/attributes/restore/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(GetAttributeResponse),
    summary="Restore an attribute",
    description="Restore an attribute by its ID.",
)
@with_session_management
async def restore_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(..., alias="attributeId")],
) -> dict:
    return await _restore_attribute(db, attribute_id)


@router.post(
    "/attributes/addTag/{attributeId}/{tagId}/local:{local}",
    status_code=status.HTTP_200_OK,
    response_model=partial(AddRemoveTagAttributeResponse),
    summary="Add tag to attribute",
    description="Add a tag to an attribute by there ids.",
)
@with_session_management
async def add_tag_to_attribute(
    local: str,
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(..., alias="attributeId")],
    tag_id: Annotated[str, Path(..., alias="tagId")],
) -> dict:
    return await _add_tag_to_attribute(db, attribute_id, tag_id, local)


@router.post(
    "/attributes/removeTag/{attributeId}/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(AddRemoveTagAttributeResponse),
    summary="Remove tag from attribute",
    description="Remove a tag from an attribute by there ids.",
)
@with_session_management
async def remove_tag_from_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(..., alias="attributeId")],
    tag_id: Annotated[str, Path(..., alias="tagId")],
) -> dict:
    return await _remove_tag_from_attribute(db, attribute_id, tag_id)


# - deprecated endpoints


@router.post(
    "/attributes/add/{eventId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(AddAttributeResponse),
    summary="Add new attribute (Deprecated)",
    description="Deprecated. Add a new attribute with the given details using the old route.",
)
@with_session_management
async def add_attribute_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    body: AddAttributeBody,
) -> dict:
    return await _add_attribute(db, event_id, body)


@router.get(
    "/attributes/view/{attributeId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(GetAttributeResponse),
    summary="Get attribute details (Deprecated)",
    description="Deprecated. Retrieve details of a specific attribute by its ID using the old route.",
)
@with_session_management
async def get_attribute_details_depr(
    db: Annotated[Session, Depends(get_db)], attribute_id: Annotated[str, Path(..., alias="attributeId")]
) -> dict:
    return await _get_attribute_details(db, attribute_id)


@router.put(
    "/attributes/edit/{attributeId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(EditAttributeResponse),
    summary="Update an attribute (Deprecated)",
    description="Deprecated. Update an existing attribute by its ID using the old route.",
)
@with_session_management
async def update_attribute_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(..., alias="attributeId")],
    body: EditAttributeBody,
) -> dict:
    return await _update_attribute(db, attribute_id, body)


@router.delete(
    "/attributes/delete/{attributeId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=DeleteAttributeResponse,
    summary="Delete an Attribute (Deprecated)",
    description="Deprecated. Delete an attribute by its ID using the old route.",
)
@with_session_management
async def delete_attribute_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(..., alias="attributeId")],
) -> dict:
    return await _delete_attribute(db, attribute_id)


# --- endpoint logic ---


async def _add_attribute(db: Session, event_id: str, body: AddAttributeBody) -> dict:
    event: Event | None = db.get(Event, event_id)

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
    db.commit()

    db.refresh(new_attribute)
    setattr(event, "attribute_count", event.attribute_count + 1)

    attribute_data = _prepare_attribute_response(new_attribute, "add")

    return AddAttributeResponse(Attribute=attribute_data).__dict__


async def _get_attribute_details(db: Session, attribute_id: str) -> dict:
    attribute: Attribute | None = db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    attribute_data = _prepare_get_attribute_details_response(db, attribute_id, attribute)

    return GetAttributeResponse(Attribute=attribute_data).__dict__


async def _update_attribute(db: Session, attribute_id: str, body: EditAttributeBody) -> dict:
    attribute: Attribute | None = db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    update_record(attribute, body.dict())

    db.commit()
    db.refresh(attribute)

    attribute_data = _prepare_edit_attribute_response(db, attribute_id, attribute)

    return EditAttributeResponse(Attribute=attribute_data).__dict__


async def _delete_attribute(db: Session, attribute_id: str) -> dict:
    attribute: Attribute | None = db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(attribute)
    db.commit()

    return DeleteAttributeResponse(message="Attribute deleted.").__dict__


async def _get_attributes(db: Session) -> list[dict]:
    attributes = db.query(Attribute).all()

    if not attributes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attributes found.")

    attribute_responses = [_prepare_attribute_response(attribute, "get all") for attribute in attributes]

    return attribute_responses


async def _delete_selected_attributes(
    db: Session, event_id: str, body: DeleteSelectedAttributeBody, request: Request
) -> dict:
    event: Event | None = db.get(Event, event_id)

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    attribute_ids = body.id.split(" ")

    for attribute_id in attribute_ids:
        attribute: Attribute | None = db.get(Attribute, attribute_id)

        if not attribute:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        if not attribute.event.id == int(event_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No attribute with id '{attribute_id}' found in the given event.",
            )

        if body.allow_hard_delete:
            db.delete(attribute)
            db.commit()
        else:
            setattr(attribute, "deleted", True)
            db.commit()

            db.refresh(attribute)

    attribute_count = len(attribute_ids)
    attribute_str = "attribute" if attribute_count == 1 else "attributes"

    return DeleteSelectedAttributeResponse(
        saved=True,
        success=True,
        name=f"{attribute_count} {attribute_str} deleted.",
        message=f"{attribute_count} {attribute_str} deleted.",
        url=str(request.url.path),
        id=str(event_id),
    ).__dict__


async def _rest_search_attributes(db: Session, body: SearchAttributesBody) -> dict:
    if body.returnFormat != "json":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid output format.")
    attributes: list[Attribute] = db.query(Attribute).all()
    for field, value in body.dict().items():
        attribute_dict = db.query(Attribute).__dict__.copy()
        if field not in attribute_dict:
            continue
        attributes = db.query(Attribute).filter(getattr(Attribute, field) == value).all()

        #! todo: not all fields in 'SearchAttributesBody' are taken into account yet
    if body.limit is not None:
        attributes = attributes[: body.limit]
    response_list = []
    for attribute in attributes:
        attribute_dict = attribute.asdict().copy()
        if attribute.event_id is not None:
            event = db.get(Event, attribute.event_id)
            event_dict = event.__dict__.copy()
            event_dict["date"] = str(event_dict["date"])
            attribute_dict["Event"] = SearchAttributesEvent(**event_dict)
        if attribute.object_id != 0:
            object = db.get(Object, attribute.object_id)
            object_dict = object.__dict__.copy()
            attribute_dict["Object"] = SearchAttributesObject(**object_dict)
        attribute_tags = db.query(AttributeTag).filter(AttributeTag.attribute_id == attribute.id).all()
        attribute_dict["Tag"] = []
        for attribute_tag in attribute_tags:
            tag = db.get(Tag, attribute_tag.tag_id)
            tag_dict = tag.__dict__.copy()
            tag_dict["local"] = attribute_tag.local
            attribute_dict["Tag"].append(GetAttributeTag(**tag_dict))

        response_list.append(SearchAttributesAttributes(Attribute=SearchAttributesAttributesDetails(**attribute_dict)))

    return SearchAttributesResponse(response=response_list).__dict__


async def _get_attribute_statistics(
    db: Session, context: str, percentage: int
) -> GetAttributeStatisticsTypesResponse | GetAttributeStatisticsCategoriesResponse:
    if context not in ["type", "category"]:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Invalid 'context'")
    if int(percentage) not in [0, 1]:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Invalid 'percentage'")

    total_count_of_attributes = db.query(Attribute).count()

    if context == "category":
        return _category_statistics(db, percentage, total_count_of_attributes)
    else:
        return _type_statistics(db, percentage, total_count_of_attributes)


async def _restore_attribute(db: Session, attribute_id: str) -> dict:
    attribute: Attribute | None = db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    setattr(attribute, "deleted", False)

    db.commit()

    db.refresh(attribute)

    attribute_data = _prepare_get_attribute_details_response(db, str(attribute.id), attribute)

    return GetAttributeResponse(Attribute=attribute_data).__dict__


async def _add_tag_to_attribute(db: Session, attribute_id: str, tag_id: str, local: str) -> dict:
    attribute: Attribute | None = db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    try:
        int(tag_id)
    except ValueError:
        return AddRemoveTagAttributeResponse(saved=False, errors="Invalid Tag").__dict__
    if not db.get(Tag, tag_id):
        return AddRemoveTagAttributeResponse(saved=False, errors="Tag could not be added.").__dict__

    tag = db.get(Tag, tag_id)

    if int(local) not in [0, 1]:
        return AddRemoveTagAttributeResponse(saved=False, errors="Invalid 'local'").__dict__
    local_output = local != "0"

    new_attribute_tag = AttributeTag(
        attribute_id=attribute.id, event_id=attribute.event_id, tag_id=tag.id, local=local_output
    )

    db.add(new_attribute_tag)
    db.commit()

    db.refresh(new_attribute_tag)

    return AddRemoveTagAttributeResponse(saved=True, success="Tag added", check_publish=True).__dict__


async def _remove_tag_from_attribute(db: Session, attribute_id: str, tag_id: str) -> dict:
    attribute: Attribute | None = db.get(Attribute, attribute_id)

    if not attribute:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    try:
        int(tag_id)
    except ValueError:
        return AddRemoveTagAttributeResponse(saved=False, errors="Invalid Tag").__dict__
    if not db.get(Tag, tag_id):
        return AddRemoveTagAttributeResponse(saved=False, errors="Tag could not be removed.").__dict__

    attribute_tag = db.query(AttributeTag).filter(AttributeTag.attribute_id == attribute_id).first()

    if not attribute_tag:
        return AddRemoveTagAttributeResponse(saved=False, errors="Invalid attribute - tag combination.").__dict__

    db.delete(attribute_tag)
    db.commit()

    return AddRemoveTagAttributeResponse(saved=True, success="Tag removed", check_publish=True).__dict__


def _prepare_attribute_response(attribute: Attribute, request_type: str) -> dict[str, Any]:
    attribute_dict = attribute.asdict().copy()

    fields_to_convert = ["object_id", "sharing_group_id"]
    for field in fields_to_convert:
        attribute_dict[field] = str(attribute_dict.get(field, "0"))

    response_strategy = {"add": AddAttributeAttributes, "get all": GetAllAttributesResponse}

    response_class = response_strategy.get(request_type)

    if response_class:
        return response_class(**attribute_dict).dict()

    raise ValueError(f"Unknown request_type: {request_type}")


def _prepare_get_attribute_details_response(
    db: Session, attribute_id: str, attribute: Attribute
) -> GetAttributeAttributes:
    attribute_dict = attribute.asdict().copy()
    if "event_uuid" not in attribute_dict.keys():  #! should not occur, perhaps sqlalchemy caching?
        attribute_dict["event_uuid"] = attribute.event_uuid

    fields_to_convert = ["object_id", "sharing_group_id", "timestamp"]
    for field in fields_to_convert:
        if attribute_dict.get(field) is not None:
            attribute_dict[field] = str(attribute_dict[field])
        else:
            attribute_dict[field] = "0"

    db_attribute_tags = db.query(AttributeTag).filter(AttributeTag.attribute_id == attribute_id).all()
    attribute_dict["tag"] = []

    if len(db_attribute_tags) > 0:
        for attribute_tag in db_attribute_tags:
            tag = db.query(Tag).filter(Tag.id == attribute_tag.tag_id).first()
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


def _prepare_edit_attribute_response(db: Session, attribute_id: str, attribute: Attribute) -> EditAttributeAttributes:
    attribute_dict = attribute.asdict().copy()

    fields_to_convert = ["object_id", "sharing_group_id", "timestamp"]
    for field in fields_to_convert:
        if attribute_dict.get(field) is not None:
            attribute_dict[field] = str(attribute_dict[field])
        else:
            attribute_dict[field] = "0"

    db_attribute_tags = db.query(AttributeTag).filter(AttributeTag.attribute_id == attribute_id).all()
    attribute_dict["tag"] = []

    if len(db_attribute_tags) > 0:
        for attribute_tag in db_attribute_tags:
            tag = db.query(Tag).filter(Tag.id == attribute_tag.tag_id).first()
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
                local_only=tag.local_only,
            )
            attribute_dict["tag"].append(connected_tag)

    return EditAttributeAttributes(**attribute_dict)


def _category_statistics(
    db: Session, percentage: int, total_count_of_attributes: int
) -> GetAttributeStatisticsCategoriesResponse:
    response_dict = {}

    for category in GetDescribeTypesAttributes().categories:
        if percentage == 1:
            response_dict[category] = (
                str(
                    round((_count_of_attributes_with_given_category(db, category) / total_count_of_attributes) * 100, 2)
                )
                + "%"
            )
        else:
            response_dict[category] = str(_count_of_attributes_with_given_category(db, category))

    return GetAttributeStatisticsCategoriesResponse(**response_dict)


def _type_statistics(
    db: Session, percentage: int, total_count_of_attributes: int
) -> GetAttributeStatisticsTypesResponse:
    response_dict = {}

    for type in GetDescribeTypesAttributes().types:
        if percentage == 1:
            response_dict[type] = (
                str(round((_count_of_attributes_with_given_type(db, type) / total_count_of_attributes) * 100, 2)) + "%"
            )
        else:
            response_dict[type] = str(_count_of_attributes_with_given_type(db, type))

    return GetAttributeStatisticsTypesResponse(**response_dict)


def _count_of_attributes_with_given_category(db: Session, category: str) -> int:
    attributes_with_given_category = db.query(Attribute).filter(Attribute.category == category).all()
    return len(attributes_with_given_category)


def _count_of_attributes_with_given_type(db: Session, type: str) -> int:
    attributes_with_given_type = db.query(Attribute).filter(Attribute.type == type).all()
    return len(attributes_with_given_type)
