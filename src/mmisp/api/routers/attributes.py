from fastapi import APIRouter, Depends
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
from mmisp.api_schemas.attributes.get_attribute_statistics_response import GetAttributeStatisticsTypesResponse
from mmisp.api_schemas.attributes.get_describe_types_response import GetDescribeTypesResponse
from mmisp.api_schemas.attributes.restore_attribute_reponse import RestoreAttributeResponse
from mmisp.api_schemas.attributes.search_attributes_body import SearchAttributesBody
from mmisp.api_schemas.attributes.search_attributes_response import SearchAttributesResponse
from mmisp.db.database import get_db

router = APIRouter(tags=["attributes"])


# -- Delete


@router.delete("/attributes/delete/{attribute_id}", summary="Delete an Attribute", deprecated=True)  # deprecated
@router.delete("/attributes/{attributeID}", summary="Delete an Attribute")  # new
async def attributes_delete(attribute_id: str, db: Session = Depends(get_db)) -> DeleteAttributeResponse:
    return DeleteAttributeResponse(message="Attribute deleted.")


# -- Get


@router.get("/attributes", summary="Get all Attributes")
async def attributes_get(db: Session = Depends(get_db)) -> GetAllAttributesResponse:
    return GetAllAttributesResponse(attribute=[])
    # try:
    #     attributes = db.query(Attribute).all()
    #     return attributes
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


@router.get("/attributes/view/{attribute_id}", summary="Get an Attribute by its ID", deprecated=True)  # deprecated
@router.get("/attributes/{attribute_id}", summary="Get an Attribute by its ID")  # new
async def attributes_getById(attribute_id: str, db: Session = Depends(get_db)) -> GetAttributeResponse:
    return GetAttributeResponse(Tag=[])
    # attribute = (
    #     db.query(AttributeGetById).filter(AttributeGetById.id == attribute_id).first()
    # )
    # if attribute is None:
    #     raise HTTPException(status_code=404, detail="Feed not found")
    # return attribute


@router.get(
    "/attributes/attributeStatistics/{context}/{percentage}",
    summary="Get the count/percentage of attributes per category/type",
)
async def attributes_statistics(
    context: str, percentage: int, db: Session = Depends(get_db)
) -> GetAttributeStatisticsTypesResponse:
    return GetAttributeStatisticsTypesResponse()


@router.get("/attributes/describeTypes", summary="Get all available attribute types")
async def attributes_describeTypes(db: Session = Depends(get_db)) -> GetDescribeTypesResponse:
    return GetDescribeTypesResponse()


# -- Post


@router.post("/attributes/restSearch", summary="Get a filtered and paginated list of attributes")
async def attributes_reastSearch(body: SearchAttributesBody, db: Session = Depends(get_db)) -> SearchAttributesResponse:
    return SearchAttributesResponse(id="")


@router.post("/attributes/add/{event_id}", summary="Add an attribute", deprecated=True)  # deprecated
@router.post("/attributes/{event_id}", summary="Add an attribute")  # new
async def attributes_post(event_id: str, body: AddAttributeBody, db: Session = Depends(get_db)) -> AddAttributeResponse:
    return AddAttributeResponse(id="")
    # new_attribute = Attribute(**attribute_data.model_dump())
    # db.add(new_attribute)
    # db.commit()
    # db.refresh(new_attribute)
    # return new_attribute


@router.post("/attributes/deleteSelected/{event_id}", summary="Delete the selected attributes")
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


@router.post("/attributes/restore/{attribute_id}", summary="Restore an attribute")
async def attributes_restore(attribute_id: str, db: Session = Depends(get_db)) -> RestoreAttributeResponse:
    return RestoreAttributeResponse(id="")


@router.post("/attributes/addTag/{attribute_id}/{tag_id}/local:{local}", summary="Add a tag to an attribute")
async def attributes_addTag(
    attribute_id: str, tag_id: str, local: int, db: Session = Depends(get_db)
) -> AddRemoveTagAttributeResponse:
    return AddRemoveTagAttributeResponse(
        saved=True, success="Tag added", check_publish=True, errors="Tag could not be added."
    )


@router.post("/attributes/removeTag/{attribute_id}/{tag_id}", summary="Remove a tag from an attribute")
async def attributes_removeTag(
    attribute_id: str, tag_id: str, db: Session = Depends(get_db)
) -> AddRemoveTagAttributeResponse:
    return AddRemoveTagAttributeResponse(
        saved=True, success="Tag added", check_publish=True, errors="Tag could not be added."
    )


# -- Put


@router.put("/attributes/edit/{attribute_id}", summary="Edit an attribute", deprecated=True)  # deprecated
@router.put("/attributes/{attribute_id}", summary="Edit an attribute")  # new
async def attributes_put(
    attribute_id: str, body: EditAttributeBody, db: Session = Depends(get_db)
) -> EditAttributeResponse:
    return EditAttributeResponse(id="")
