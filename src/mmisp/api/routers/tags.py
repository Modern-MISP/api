from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# from ..models.tag import Tag
from ...db.database import get_db
from ...api_schemas.tags.create_update_tag_body import TagCreateAndUpdateBody
from ...api_schemas.tags.delete_tag_response import TagDeleteResponse
from ...api_schemas.tags.get_tag_response import TagAttributesResponse, TagGetResponse
from ...api_schemas.tags.search_tags_response import TagSearchResponse

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", summary="Get all tags", description="Retrieve a list of all tags.")
async def get_tags(db: Session = Depends(get_db)) -> TagGetResponse:
    # Logic to get tags goes here

    return TagGetResponse(tag=[])


@router.get(
    "/view/{tagId}",
    deprecated=True,
    summary="View tag details (Deprecated)",
    description="Deprecated. View details of a specific tag using the old route.",
)
@router.get(
    "/{tagId}",
    summary="View tag details",
    description="View details of a specific tag.",
)
async def view_tag(tag_id: str, db: Session = Depends(get_db)) -> TagAttributesResponse:
    # Logic to view tag details goes here

    return TagAttributesResponse(
        id="",
        name="",
        colour="",
        exportable=False,
        org_id="",
        user_id="",
        hide_tag=False,
        numerical_value="",
        is_galaxy=False,
        is_custom_galaxy=False,
        inherited=0,
        attribute_count=0,
        count=0,
        favourite=False,
        local_only=False,
    )


@router.post(
    "/add",
    deprecated=True,
    summary="Add new tag (Deprecated)",
    description="Deprecated. Add a new tag using the old route.",
)
@router.post(
    "/", summary="Add new tag", description="Add a new tag with given details."
)
async def add_tag(
    body: TagCreateAndUpdateBody, db: Session = Depends(get_db)
) -> TagGetResponse:
    # Logic to add a new tag goes here

    return TagGetResponse(tag=[])


@router.post(
    "/delete/{tagId}",
    deprecated=True,
    summary="Delete tag (Deprecated)",
    description="Deprecated. Delete a specific tag using the old route.",
)
@router.delete("/{tagId}", summary="Delete tag", description="Delete a specific tag.")
async def delete_tag(tag_id: str, db: Session = Depends(get_db)) -> TagDeleteResponse:
    # Logic to delete a tag goes here

    return TagDeleteResponse(name="", message="", url="")


@router.post(
    "/edit/{tagId}",
    deprecated=True,
    summary="Edit tag (Deprecated)",
    description="Deprecated. Edit a specific tag using the old route.",
)
@router.put(
    "/{tagId}", summary="Edit tag", description="Edit details of a specific tag."
)
async def edit_tag(
    tag_id: str, body: TagCreateAndUpdateBody, db: Session = Depends(get_db)
) -> TagGetResponse:
    # Logic to edit a tag goes here

    return TagGetResponse(tag=[])


@router.get(
    "/search/{tagSearchTerm}",
    summary="Search tags",
    description="Search for tags using a specific search term.",
)
async def search_tags(
    tagSearchTerm: str, db: Session = Depends(get_db)
) -> TagSearchResponse:
    # Logic to search tags goes here

    return TagSearchResponse(root=[])
