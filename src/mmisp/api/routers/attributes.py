from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from mmisp.api_schemas.attributes.add_attribute_body import AddAttributeBody
from mmisp.api_schemas.attributes.add_attribute_response import AddAttributeResponse
from mmisp.api_schemas.attributes.add_remove_tag_attribute_response import AddRemoveTagAttributeResponse
from mmisp.api_schemas.attributes.delete_attribute_response import DeleteAttributeResponse
from mmisp.api_schemas.attributes.delete_selected_attribute_body import DeleteSelectedAttributeBody
from mmisp.api_schemas.attributes.delete_selected_attribute_response import DeleteSelectedAttributeResponse
from mmisp.api_schemas.attributes.edit_attribute_body import EditAttributeBody
from mmisp.api_schemas.attributes.edit_attributes_response import EditAttributeResponse
from mmisp.api_schemas.attributes.get_all_attributes_response import GetAllAttributesResponse
from mmisp.api_schemas.attributes.get_attribute_response import GetAttributeResponse
from mmisp.api_schemas.attributes.get_attribute_statistics_response import GetAttributeStatisticsCategoriesResponse
from mmisp.api_schemas.attributes.get_describe_types_response import GetDescribeTypesResponse
from mmisp.api_schemas.attributes.restore_attribute_reponse import RestoreAttributeResponse
from mmisp.api_schemas.attributes.search_attributes_body import SearchAttributesBody
from mmisp.api_schemas.attributes.search_attributes_response import SearchAttributesResponse
from mmisp.db.database import get_db
from mmisp.db.models.attribute import Attribute

router = APIRouter(tags=["attributes"])


# Sorted according to CRUD

# - Create a {resource}


@router.post("/attributes/add/{eventId}", summary="Add an attribute", deprecated=True)  # deprecated
@router.post("/attributes/{eventId}", summary="Add an attribute")  # new
async def attributes_post(event_id: str, body: AddAttributeBody, db: Session = Depends(get_db)) -> AddAttributeResponse:
    new_attribute = Attribute(
        value=body.value,
        type=body.type,
        category=body.category,
        to_ids=body.to_ids,
        distribution=body.distribution,
        comment=body.comment,
        disable_correlation=body.disable_correlation,
    )
    db.add(new_attribute)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    db.refresh(new_attribute)
    return AddAttributeResponse(
        id=str(new_attribute.id),
        event_id=str(event_id),
        object_id=str(new_attribute.object_id),
        object_relation=str(new_attribute.object_relation),
        category=str(new_attribute.category),
        type=str(new_attribute.type),
        value=str(new_attribute.value),
        value1=str(new_attribute.value1),
        value2=str(new_attribute.value2),
        to_ids=bool(new_attribute.to_ids),
        uuid=str(new_attribute.uuid),
        timestamp=str(new_attribute.timestamp),
        distribution=str(new_attribute.distribution),
        sharing_group_id=str(new_attribute.sharing_group_id),
        comment=str(new_attribute.comment),
        deleted=bool(new_attribute.deleted),
        disable_correlation=bool(new_attribute.disable_correlation),
        first_seen=str(new_attribute.first_seen),
        last_seen=str(new_attribute.last_seen),
        AttributeTag=[],
    )


# - Read / Get a {resource}


@router.get("/attributes/view/{attributeId}", summary="Get an Attribute by its ID", deprecated=True)  # deprecated
@router.get("/attributes/{attributeId}", summary="Get an Attribute by its ID")  # new
async def attributes_getBy_id(attribute_id: str, db: Session = Depends(get_db)) -> GetAttributeResponse:
    return GetAttributeResponse()
    # attribute = (
    #     db.query(AttributeGetBy_id).filter(AttributeGetBy_id.id == attribute_id).first()
    # )
    # if attribute is None:
    #     raise HTTPException(status_code=404, detail="Feed not found")
    # return attribute


# - Updating a {resource}


@router.put("/attributes/edit/{attributeId}", summary="Edit an attribute", deprecated=True)  # deprecated
@router.put("/attributes/{attributeId}", summary="Edit an attribute")  # new
async def attributes_put(
    attribute_id: str, body: EditAttributeBody, db: Session = Depends(get_db)
) -> EditAttributeResponse:
    return EditAttributeResponse()


# - Deleting a {resource}


@router.delete("/attributes/delete/{attributeId}", summary="Delete an Attribute", deprecated=True)  # deprecated
@router.delete("/attributes/{attributeID}", summary="Delete an Attribute")  # new
async def attributes_delete(attribute_id: str, db: Session = Depends(get_db)) -> DeleteAttributeResponse:
    return DeleteAttributeResponse(message="Attribute deleted.")


# - Get all {resource}s


@router.get("/attributes", summary="Get all Attributes")
async def attributes_get(db: Session = Depends(get_db)) -> list[GetAllAttributesResponse]:
    return list[GetAllAttributesResponse()]
    # try:
    #     attributes = db.query(Attribute).all()
    #     return attributes
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


# - More niche endpoints


@router.post("/attributes/deleteSelected/{eventId}", summary="Delete the selected attributes")
async def attributes_deleteSelected(
    event_id: str, body: DeleteSelectedAttributeBody, db: Session = Depends(get_db)
) -> DeleteSelectedAttributeResponse:
    return DeleteSelectedAttributeResponse(
        saved=True,
        success=True,
        name="1 attribute deleted",
        message="1 attribute deleted",
        url="/attributes/deleteSelected/{event_id}",
        id="{event_id}",
    )


@router.post("/attributes/restSearch", summary="Get a filtered and paginated list of attributes")
async def attributes_reastSearch(body: SearchAttributesBody, db: Session = Depends(get_db)) -> SearchAttributesResponse:
    return SearchAttributesResponse()


@router.get(
    "/attributes/attributeStatistics/{context}/{percentage}",
    summary="Get the count/percentage of attributes per category/type",
)
async def attributes_statistics(
    context: str, percentage: int, db: Session = Depends(get_db)
) -> GetAttributeStatisticsCategoriesResponse:
    return GetAttributeStatisticsCategoriesResponse()
    # response = {}
    # for type in GetDescribeTypesAttributes().types:
    #     response.update({type: str(percentage)})
    # return response


@router.get("/attributes/describeTypes", summary="Get all available attribute types")
async def attributes_describeTypes(db: Session = Depends(get_db)) -> GetDescribeTypesResponse:
    return GetDescribeTypesResponse()


@router.post("/attributes/restore/{attributeId}", summary="Restore an attribute")
async def attributes_restore(attribute_id: str, db: Session = Depends(get_db)) -> RestoreAttributeResponse:
    return RestoreAttributeResponse(id="")


@router.post("/attributes/addTag/{attributeId}/{tagId}/local:{local}", summary="Add a tag to an attribute")
async def attributes_addTag(
    attribute_id: str, tag_id: str, local: int, db: Session = Depends(get_db)
) -> AddRemoveTagAttributeResponse:
    return AddRemoveTagAttributeResponse(
        saved=True, success="Tag added", check_publish=True, errors="Tag could not be added."
    )


@router.post("/attributes/removeTag/{attributeId}/{tagId}", summary="Remove a tag from an attribute")
async def attributes_removeTag(
    attribute_id: str, tag_id: str, db: Session = Depends(get_db)
) -> AddRemoveTagAttributeResponse:
    return AddRemoveTagAttributeResponse(
        saved=True, success="Tag removed", check_publish=True, errors="Tag could not be removed."
    )
