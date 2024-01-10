from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.event import Event
from ..models.object import Object
from ..models.tag import Tag
from ..schemas.attributes.attribute_schema import AttributeSchema
from ..schemas.attributes.delete_attribute_response import AttributeDeleteResponse
from ..schemas.attributes.get_all_attributes_response import AttributesResponse
from ..schemas.attributes.get_attribute_response import AttributeResponse
from ..schemas.attributes.get_attribute_statistics_response import (
    AttributeStatisticsResponse,
)
from ..schemas.attributes.get_describe_types_response import DescribeTypesResponse

router = APIRouter(prefix="/attributes", tags=["attributes"])


# -- Delete


@router.delete("/delete/{attribute_id}", deprecated=True)  # deprecated
@router.delete("/{attributeID}")  # new
async def attributes_delete() -> AttributeDeleteResponse:
    return AttributeDeleteResponse(message="Attribute deleted.")


# -- Get


@router.get("/attributes")
async def attributes_get(db: Session = Depends(get_db)) -> AttributesResponse:
    return AttributesResponse(attribute=[])
    """
    try:
        attributes = db.query(Attribute).all()
        return attributes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    """


@router.get("/view/{attribute_id}", deprecated=True)  # deprecated
@router.get("/{attribute_id}")  # new
async def attributes_getById(
    attribute_id: str,
    db: Session = Depends(get_db),
) -> AttributeResponse:
    return AttributeResponse(Tag=[])
    """
    attribute = (
        db.query(AttributeGetById).filter(AttributeGetById.id == attribute_id).first()
    )
    if attribute is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    return attribute
    """


@router.get("/attributeStatistics/{context}/{percentage}")
async def attributes_statistics(
    context: str, percentage: int, db: Session = Depends(get_db)
) -> AttributeStatisticsResponse:
    return (
        '"[Type/Category]": "[Count/Percentage of attributes with this type/category]"'
    )


@router.get("/describeTypes")
async def attributes_describeTypes(
    db: Session = Depends(get_db),
) -> DescribeTypesResponse:
    return "[List all attribute categories and types]"


# -- Post


@router.post("/restSearch")
async def attributes_reastSearch(
    db: Session = Depends(get_db),
) -> List[str]:
    return str, Event, Object, Tag


@router.post("/add/{event_id}")
@router.post("/{event_id}")
async def attributes_post(
    value: str,
    type: str,
    category: str,
    to_ids: bool,
    distribution: str,
    comment: str,
    disable_correlation: bool,
    attribute_data: AttributeSchema,
    db: Session = Depends(get_db),
) -> str:
    return str

    """
    new_attribute = Attribute(**attribute_data.model_dump())
    db.add(new_attribute)
    db.commit()
    db.refresh(new_attribute)
    return new_attribute
    """


@router.post("/deleteSelected/{event_id}")
async def attributes_deleteSelected(
    id: str, event_id: str, allow_hard_delete: bool, db: Session = Depends(get_db)
) -> str:
    return '"saved": true, \n "success": true, \n "name": "1 attribute deleted.", \n "message": "1 attribute deleted.", \n "url": "/deleteSelected/{\event_id}", \n "id": "{\event_id}"'


@router.post("/restore/{attribute_id}")
async def attributes_restore(db: Session = Depends(get_db)) -> str:
    return str


@router.post(
    "/addTag/{attribute_id}/{tag_id}/local:{local}",
)
async def attributes_addTag(db: Session = Depends(get_db)) -> str:
    return '"saved": true, \n "success": "Tag added.", \n "check_publish": true'


@router.post("/removeTag/{attribute_id}/{tag_id}")
async def attributes_removeTag(db: Session = Depends(get_db)) -> str:
    return '"saved": true, \n "success": "Tag removed.", \n "check_publish": true'


# -- Put


@router.put("/edit/{attribute_id}")
@router.put("/{attribute_id}")
async def attributes_put(
    category: str,
    value: str,
    to_ids: bool,
    distribution: str,
    comment: str,
    disable_correlation: bool,
    db: Session = Depends(get_db),
) -> str:
    return str
