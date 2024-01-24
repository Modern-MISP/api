from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# from ..models.object import Object
from mmisp.api_schemas.objects.create_object_body import ObjectCreateBody
from mmisp.api_schemas.objects.delete_object_response import ObjectDeleteResponse
from mmisp.api_schemas.objects.get_added_object_response import ObjectGetAddedResponse
from mmisp.api_schemas.objects.get_object_response import ObjectViewResponse, ObjectWithAttributesAndEventSearchResponse
from mmisp.api_schemas.objects.search_objects_body import ObjectSearchBody
from mmisp.api_schemas.objects.search_objects_response import ObjectSearchResponse, ObjectWithAttributesSearchResponse
from mmisp.db.database import get_db

router = APIRouter(prefix="/objects", tags=["objects"])


# Sorted according to CRUD


@router.post("/restsearch", summary="Search objects", description="Search for objects based on various filters.")
async def restsearch(body: ObjectSearchBody, db: Session = Depends(get_db)) -> ObjectSearchResponse:
    # Logic to search objects goes here

    return ObjectSearchResponse(response=[])


@router.post(
    "/add/{eventId}/{objectTemplateId}",
    deprecated=True,
    summary="Add object to event (Deprecated)",
    description="Deprecated. Add an object to an event using the old route.",
)
@router.post(
    "/{eventId}/{objectTemplateId}",
    summary="Add object to event",
    description="Add a new object to a specific event using a template.",
)
async def add_object(
    event_id: str, object_template_id: str, body: ObjectCreateBody, db: Session = Depends(get_db)
) -> ObjectGetAddedResponse:
    # Logic to add an object goes here

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


@router.get(
    "/view/{objectId}",
    deprecated=True,
    summary="View object details (Deprecated)",
    description="Deprecated. View details of a specific object using the old route.",
)
@router.get(
    "/{objectId}",
    summary="View object details",
    description="View details of a specific object including its attributes and related event.",
)
async def get_object_details(object_id: str, db: Session = Depends(get_db)) -> ObjectViewResponse:
    # Logic to get object details goes here

    return ObjectViewResponse(
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


@router.delete(
    "/delete/{objectId}/{hardDelete}",
    deprecated=True,
    summary="Delete object (Deprecated)",
    description="""
    Deprecated. Delete a specific object using the old route.
    The hardDelete parameter determines if it's a hard or soft delete.""",
)
@router.delete(
    "/{objectId}/{hardDelete}",
    summary="Delete object",
    description="Delete a specific object. The hardDelete parameter determines if it's a hard or soft delete.",
)
async def delete_object(object_id: str, hard_delete: bool, db: Session = Depends(get_db)) -> ObjectDeleteResponse:
    # Logic to delete an object goes here

    return ObjectDeleteResponse(saved=False, success=False, name="", message="", url="")
