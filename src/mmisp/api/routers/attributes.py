import logging
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from sqlalchemy.exc import SQLAlchemyError
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
from mmisp.api_schemas.attributes.restore_attribute_reponse import RestoreAttributeResponse
from mmisp.api_schemas.attributes.search_attributes_body import SearchAttributesBody
from mmisp.api_schemas.attributes.search_attributes_response import SearchAttributesResponse
from mmisp.db.database import get_db
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.event import Event
from mmisp.db.models.tag import Tag
from mmisp.util.partial import partial
from mmisp.util.request_validations import check_existence_and_raise

router = APIRouter(tags=["attributes"])
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


# Sorted according to CRUD


# - Create a {resource}


@router.post(
    "/attributes/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(AddAttributeResponse),
    summary="Add new attribute",
    description="Add a new attribute with the given details.",
)
async def add_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    body: AddAttributeBody,
) -> dict:
    return await _add_attribute(db, event_id, body)


# - Read / Get a {resource}


@router.get(
    "/attributes/describeTypes",
    status_code=status.HTTP_200_OK,
    response_model=partial(GetDescribeTypesResponse),
    summary="Get all available attribute types",
)
async def get_attributes_describe_types() -> GetDescribeTypesResponse:
    return GetDescribeTypesResponse(result=GetDescribeTypesAttributes())


@router.get(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    # response_model=partial(GetAttributeResponse),
    summary="Get attribute details",
    description="Retrieve details of a specific attribute by its ID.",
)  # new
async def get_attribute_details(
    db: Annotated[Session, Depends(get_db)], attribute_id: Annotated[str, Path(..., alias="attributeId")]
) -> dict:
    # if attribute_id == "describeTypes":
    #     return await get_attributes_describe_types()
    # else:
    return await _get_attribute_details(db, attribute_id)


# - Updating a {resource}


@router.put(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(EditAttributeResponse),
    summary="Edit an attribute",
)  # new
async def update_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(..., alias="attributeId")],
    body: EditAttributeBody,
) -> dict:
    return await _update_attribute(db, attribute_id, body)


# - Deleting a {resource}


@router.delete(
    "/attributes/{attributeId}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteAttributeResponse,
    summary="Delete an Attribute",
)  # new
async def delete_attribute(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    attribute_id: Annotated[str, Path(..., alias="attributeId")],
) -> dict:
    return await _delete_attribute(db, attribute_id)


# - Get all {resource}s


@router.get(
    "/attributes",
    status_code=status.HTTP_200_OK,
    response_model=list[partial(GetAllAttributesResponse)],
    summary="Get all Attributes",
)
async def get_attributes(db: Annotated[Session, Depends(get_db)]) -> dict:
    return await _get_attributes(db)
    # try:
    #     attributes = db.query(Attribute).all()
    #     return attributes
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


# - More niche endpoints


@router.post(
    "/attributes/deleteSelected/{eventId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(DeleteSelectedAttributeResponse),
    summary="Delete the selected attributes",
)
async def delete_selected_attributes(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    event_id: Annotated[str, Path(..., alias="eventId")],
    body: DeleteSelectedAttributeBody,
    request: Request,
) -> dict:
    return await _delete_selected_attributes(db, event_id, body, request)


@router.post("/attributes/restSearch", summary="Get a filtered and paginated list of attributes")
async def rest_search(body: SearchAttributesBody, db: Session = Depends(get_db)) -> SearchAttributesResponse:
    return SearchAttributesResponse()


@router.get(
    "/attributes/attributeStatistics/{context}/{percentage}",
    status_code=status.HTTP_200_OK,
    summary="Get the count/percentage of attributes per category/type",
)
async def get_attributes_statistics(db: Annotated[Session, Depends(get_db)], context: str, percentage: int) -> dict:
    return _get_attribute_statistics(db, context, percentage)


@router.post("/attributes/restore/{attributeId}", summary="Restore an attribute")
async def restore_attribute(attribute_id: str, db: Session = Depends(get_db)) -> RestoreAttributeResponse:
    return RestoreAttributeResponse(id="")


@router.post("/attributes/addTag/{attributeId}/{tagId}/local:{local}", summary="Add a tag to an attribute")
async def add_tag_to_attribute(
    attribute_id: str, tag_id: str, local: int, db: Session = Depends(get_db)
) -> AddRemoveTagAttributeResponse:
    return AddRemoveTagAttributeResponse(
        saved=True, success="Tag added", check_publish=True, errors="Tag could not be added."
    )


@router.post("/attributes/removeTag/{attributeId}/{tagId}", summary="Remove a tag from an attribute")
async def remove_tag_from_attribute(
    attribute_id: str, tag_id: str, db: Session = Depends(get_db)
) -> AddRemoveTagAttributeResponse:
    return AddRemoveTagAttributeResponse(
        saved=True, success="Tag removed", check_publish=True, errors="Tag could not be removed."
    )


# - Deprecated endpoints


@router.post("/attributes/add/{eventId}", summary="Add an attribute", deprecated=True)
async def add_attribute_depr() -> None:
    return None


@router.get("/attributes/view/{attributeId}", summary="Get an Attribute by its ID", deprecated=True)
async def get_attribute_details_depr() -> None:
    return None


@router.put("/attributes/edit/{attributeId}", summary="Edit an attribute", deprecated=True)
async def update_attribute_depr() -> None:
    return None


@router.delete("/attributes/delete/{attributeId}", summary="Delete an Attribute", deprecated=True)  # deprecated
async def delete_attribute_depr() -> None:
    return None


# --- endpoint logic ---


async def _add_attribute(db: Session, event_id: str, body: AddAttributeBody) -> dict:
    check_existence_and_raise(db, Event, event_id, "event_id", "Event not found.")
    if not body.value:
        if not body.value1:
            logger.error("Attribute creation failed: attribute 'value' or 'value1' is required.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'value' or 'value1' is required")
    if not body.type:
        logger.error("Attribute creation failed: attribute 'type' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'type' is required")
    if body.type not in GetDescribeTypesAttributes().types:
        logger.error("Attribute creation failed: attribute 'type' is invalid.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid 'type'")
    if body.category:
        if body.category not in GetDescribeTypesAttributes().categories:
            logger.error("Attribute creation failed: attribute 'category' is invalid.")
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

    try:
        db.add(new_attribute)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Failed to add new attribute: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    db.refresh(new_attribute)
    logger.info(f"New attribute with id = {new_attribute.id} added.")

    attribute_data = _prepare_attribute_response(new_attribute, "add")

    return AddAttributeResponse(Attribute=attribute_data)


async def _get_attribute_details(db: Session, attribute_id: str) -> dict:
    attribute = check_existence_and_raise(db, Attribute, attribute_id, "attribute_id", "Attribute not found.")

    attribute_data = prepare_get_attribute_details_response(db, attribute_id, attribute)

    return GetAttributeResponse(Attribute=attribute_data)


async def _update_attribute(db: Session, attribute_id: str, body: EditAttributeBody) -> dict:
    existing_attribute = check_existence_and_raise(db, Attribute, attribute_id, "attribute_id", "Attribute not found.")

    # event_id and event_uuid cannot be edited
    update_data = body.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(existing_attribute, key, value if not isinstance(value, Enum) else value.value)

    logger.info(existing_attribute.__dict__)

    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Failed to update attribute: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    db.refresh(existing_attribute)
    logger.info(f"Attribute with id '{existing_attribute.id}' updated.")

    attribute_data = _prepare_edit_attribute_response(db, attribute_id, existing_attribute)

    return EditAttributeResponse(Attribute=attribute_data)


async def _delete_attribute(db: Session, attribute_id: str) -> DeleteAttributeResponse:
    attribute = check_existence_and_raise(db, Attribute, attribute_id, "attribute_id", "Attribute not found.")
    try:
        db.delete(attribute)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Failed to delete attribute: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    logger.info(f"Attribute with id '{attribute_id}' deleted.")

    return DeleteAttributeResponse(message="Attribute deleted.")


async def _get_attributes(db: Session) -> dict:
    attributes = db.query(Attribute).limit(2)

    if not attributes:
        logger.error("No attributes found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attributes found.")

    attribute_responses = [_prepare_attribute_response(attribute, "get all") for attribute in attributes]

    return attribute_responses


async def _delete_selected_attributes(
    db: Session, event_id: str, body: DeleteSelectedAttributeBody, request: Request
) -> DeleteSelectedAttributeResponse:
    check_existence_and_raise(db, Event, event_id, "event_id", "Event not found.")

    attribute_ids = body.id.split(" ")

    for attribute_id in attribute_ids:
        attribute = db.get(Attribute, attribute_id)

        check_existence_and_raise(
            db, Attribute, attribute_id, "attribute_id", f"Attribute with id '{attribute_id}' not found."
        )

        if not attribute.event.id == int(event_id):
            logger.error("Failed to delete attribute: Attribute does exist, but not in the given event.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No attribute with id '{attribute_id}' found in the given event.",
            )

        if body.allow_hard_delete:
            try:
                db.delete(attribute)
                db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                logger.exception(f"Failed to delete attribute: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
                )
        else:
            setattr(attribute, "deleted", True)

    logger.info(f"Attributes with ids '{attribute_ids}' deleted.")

    if len(attribute_ids) == 1:
        return DeleteSelectedAttributeResponse(
            saved=True,
            success=True,
            name="1 attribute deleted.",
            message="1 attribute deleted.",
            url=str(request.url.path),
            id=str(event_id),
        )
    else:
        return DeleteSelectedAttributeResponse(
            saved=True,
            success=True,
            name=f"{len(attribute_ids)} attributes deleted.",
            message=f"{len(attribute_ids)} attributes deleted.",
            url=str(request.url.path),
            id=str(event_id),
        )


async def _get_attribute_statistics(db: Session, context: str, percentage: str) -> dict:
    if context not in ["type", "category"]:
        logger.exception("Get attribute statistics failed: parameter 'context' is invalid")
        HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Invalid 'context'")
    if percentage not in ["0", "1"]:
        logger.exception("Get attribute statistics failed: parameter 'percentage' is invalid")
        HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Invalid 'percentage'")

    if context == "category":
        return _category_statistics(db, percentage)
    else:
        return _type_statistics(db, percentage)


def _prepare_attribute_response(attribute: Attribute, request_type: str) -> dict:
    attribute_dict = attribute.__dict__.copy()

    fields_to_convert = ["object_id", "sharing_group_id"]
    for field in fields_to_convert:
        if attribute_dict.get(field) is not None:
            attribute_dict[field] = str(attribute_dict[field])
        else:
            attribute_dict[field] = "0"

    if request_type == "add":
        return AddAttributeAttributes(**attribute_dict)
    elif request_type == "get all":
        return GetAllAttributesResponse(**attribute_dict)


def prepare_get_attribute_details_response(
    db: Session, attribute_id: str, attribute: Attribute
) -> GetAttributeAttributes:
    attribute_dict = attribute.__dict__.copy()

    # Don't know why, but 'event_uuid' is not in attribute_dict
    attribute_dict.update({"event_uuid": attribute.event_uuid})

    fields_to_convert = ["object_id", "sharing_group_id"]
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
    attribute_dict = attribute.__dict__.copy()

    fields_to_convert = ["object_id", "sharing_group_id"]
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


def _category_statistics(db: Session, percentage: str) -> GetAttributeStatisticsCategoriesResponse:
    _count_of_attributes_with_given_category


def _type_statistics(db: Session, percentage: str) -> GetAttributeStatisticsTypesResponse:
    _count_of_attributes_with_given_type


def _count_of_attributes_with_given_category(db: Session) -> str:
    pass


def _count_of_attributes_with_given_type(db: Session) -> str:
    pass
