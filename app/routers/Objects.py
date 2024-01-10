from fastapi import APIRouter, Depends  # , HTTPException
from sqlalchemy.orm import Session

# from ..models.object import Object
from ..database import get_db
from ..schemas.objects.create_object_body import ObjectCreateBody
from ..schemas.objects.delete_object_response import ObjectDeleteResponse
from ..schemas.objects.get_added_object_response import ObjectGetAddedResponse
from ..schemas.objects.get_object_response import (
    ObjectResponse,
    ObjectWithAttributesAndEventSearchResponse,
)
from ..schemas.objects.search_objects_body import ObjectSearchBody
from ..schemas.objects.search_objects_response import (
    ObjectSearchResponse,
    ObjectWithAttributesSearchResponse,
)

router = APIRouter(prefix="/objects", tags=["objects"])


@router.post("/restsearch")
async def restsearch(
    body: ObjectSearchBody, db: Session = Depends(get_db)
) -> ObjectSearchResponse:
    return ObjectSearchResponse(response=[])


@router.post("/add/{eventId}/{objectTemplateId}", deprecated=True)  # deprecated
@router.post("/{eventId}/{objectTemplateId}")  # new
async def add_object(
    event_id: str,
    object_template_id: str,
    body: ObjectCreateBody,
    db: Session = Depends(get_db),
) -> ObjectGetAddedResponse:
    return ObjectGetAddedResponse(
        object=ObjectWithAttributesSearchResponse(
            id="",
            name="",
            meta_category="",
            description="",
            template_uuid="",
            template_version="",
            event_id="",
            uuid="",
            timestamp="",
            distribution="",
            sharing_group_id="",
            comment="",
            deleted=False,
            first_seen="",
            last_seen="",
            attributes=[],
        )
    )


@router.get("/view/{objectId}", deprecated=True)  # deprecated
@router.get("/{objectId}")  # new
async def get_feed_details(
    object_id: str, db: Session = Depends(get_db)
) -> ObjectResponse:
    return ObjectResponse(
        object=ObjectWithAttributesAndEventSearchResponse(
            id="",
            name="",
            meta_category="",
            description="",
            template_uuid="",
            template_version="",
            event_id="",
            uuid="",
            timestamp="",
            distribution="",
            sharing_group_id="",
            comment="",
            deleted=False,
            first_seen="",
            last_seen="",
            attributes=[],
            event=[],
        )
    )


@router.delete("/delete/{objectId}/{hardDelete}", deprecated=True)  # deprecated
@router.delete("/{objectId}/{hardDelete}")  # new
async def delete_object(
    objectId: str, hardDelete: bool, db: Session = Depends(get_db)
) -> ObjectDeleteResponse:
    return ObjectDeleteResponse(saved=False, success=False, name="", message="", url="")
