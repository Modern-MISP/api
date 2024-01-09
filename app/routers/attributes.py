from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.attribute import Attribute
from ..schemas.attribute_schema import (
    AttributeSchema,
    AttributeRestSearchSchema,
    AttributeAddSchema,
    AttributeEditSchema,
    AttributeDeleteSchema,
    AttributeDeleteSelectedSchema,
    AttributeTagSchema,
    AttributeGetByIdSchema,
)

# from . import events, objects, tags

router = APIRouter(prefix="/attributes")


@router.post("/restSearch", response_model=List[AttributeRestSearchSchema])
async def attributes_reastSearch(db: Session = Depends(get_db)) -> List[Attribute]:
    pass
    """
        {Attributes(), events.Events(), objects.Objects(), tags.Tags()} - {
        Attributes.value1,
        Attributes.value2,
        Attributes.event_uuid,
        Attributes.attributeTag,
    }
    """


@router.post("/add/{eventId}", response_model=AttributeAddSchema)
@router.post("/{eventId}", response_model=AttributeAddSchema)
async def attributes_post(
    value: str,
    type: str,
    category: str,
    to_ids: bool,
    distribution: str,
    comment: str,
    disable_correlation: bool,
    db: Session = Depends(get_db),
) -> Attribute:
    pass
    """
    return {Attributes} - {Attributes.event_uuid}
    """


@router.put("/edit/{attributeId}", response_model=AttributeEditSchema)
@router.put("/{attributeId}", response_model=AttributeEditSchema)
async def attributes_put(
    category: str,
    value: str,
    to_ids: bool,
    distribution: str,
    comment: str,
    disable_correlation: bool,
    db: Session = Depends(get_db),
) -> Attribute:
    pass
    """
    return {Attributes} - {Attributes.attributeTag}
    """


@router.delete("/delete/{attributeId}", response_model=AttributeDeleteSchema)
@router.delete("/{attributeID}", response_model=AttributeDeleteSchema)
async def attributes_delete() -> str:
    pass
    """
    return "message: Attribute deleted."
    """


@router.post("/deleteSelected/{event_id}", response_model=AttributeDeleteSelectedSchema)
async def attributes_deleteSelected(
    id: str, event_id: str, allow_hard_delete: bool, db: Session = Depends(get_db)
) -> str:
    pass
    """
    return (
        '"saved": true,'
        + '"success": true,'
        + '"name": "1 attribute deleted.",'
        + '"message": "1 attribute deleted.",'
        + '"url": "/deleteSelected/{event_id}",'
        + '"id": "{event_id}"'
    )
    """


@router.post("/restore/{attributeId}", response_model=AttributeEditSchema)
async def attributes_restore(db: Session = Depends(get_db)) -> Attribute:
    pass
    """
    return {Attributes} - {Attributes.attributeTag}
    """


@router.post(
    "/addTag/{attributeId}/{tagId}/local:{local}", response_model=AttributeTagSchema
)
async def attributes_addTag(db: Session = Depends(get_db)) -> str:
    pass
    """
    return '"saved": true,' + '"success": "Tag added.",' + '"check_publish": true'
    """


@router.post("/removeTag/{attributeId}/{tagId}", response_model=AttributeTagSchema)
async def attributes_removeTag(db: Session = Depends(get_db)) -> str:
    pass
    """
    return '"saved": true,' + '"success": "Tag removed.",' + '"check_publish": true'
    """


@router.get("/attributes", response_model=AttributeSchema)
async def attributes_get(db: Session = Depends(get_db)) -> Attribute:
    pass
    """
    return {Attributes} - {Attributes.event_uuid, Attributes.attributeTag}
    """


@router.get("/view/{attributeId}", response_model=AttributeGetByIdSchema)
@router.get("/{attributeId}", response_model=AttributeGetByIdSchema)
async def attributes_getById(
    attributeId: str,
    db: Session = Depends(get_db),
) -> Attribute:
    pass
    """
    return {Attributes} - {Attributes.value1, Attributes.value2}
    """


@router.get("/attributeStatistics/{context}/{percentage}", response_model=str)
async def attributes_statistics(db: Session = Depends(get_db)) -> str:
    pass
    """
    return (
        '"[Type/Category]": "[Count/Percentage of attributes with this type/category]"'
    )
    """


@router.get("/describeTypes", response_model=str)
async def attributes_describeTypes(db: Session = Depends(get_db)) -> str:
    pass
    """
    return "[List all attribute categories and types]"
    """
