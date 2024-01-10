from fastapi import APIRouter, Depends  # , HTTPException
from sqlalchemy.orm import Session

# from ..models.tag import Tag
from ..database import get_db
from ..schemas.tags.create_update_tag_body import TagCreateAndUpdateBody
from ..schemas.tags.delete_tag_response import TagDeleteResponse
from ..schemas.tags.get_tag_response import TagAttributesResponse, TagGetResponse
from ..schemas.tags.search_tags_response import TagSearchResponse

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/")
async def get_tags(db: Session = Depends(get_db)) -> TagGetResponse:
    return TagGetResponse(tag=[])


@router.get("/view/{tagId}", deprecated=True)  # deprecated
@router.get("/{tagId}")  # new
async def view_tag(tag_id: str, db: Session = Depends(get_db)) -> TagAttributesResponse:
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
        inherited=0,  # omitted
        attribute_count=0,  # new
        count=0,  # new
        favourite=False,  # new
        local_only=False,  # new
    )


@router.post("/add", deprecated=True)  # deprecated
@router.post("/")  # new
async def add_tag(
    body: TagCreateAndUpdateBody, db: Session = Depends(get_db)
) -> TagGetResponse:
    return TagGetResponse(tag=[])


@router.delete("/delete/{tagId}", deprecated=True)  # deprecated
@router.delete("/{tagId}")  # new
async def delete_tag(tag_id: str, db: Session = Depends(get_db)) -> TagDeleteResponse:
    return TagDeleteResponse(name="", message="", url="")


@router.post("/edit/{tagId}", deprecated=True)  # deprecated
@router.put("/{tagId}")  # new
async def edit_tag(
    tag_id: str, body: TagCreateAndUpdateBody, db: Session = Depends(get_db)
) -> TagGetResponse:
    return TagGetResponse(tag=[])


@router.get("search/{tagSearchTerm}")
async def search_tags(
    tagSearchTerm: str, db: Session = Depends(get_db)
) -> TagSearchResponse:
    return TagSearchResponse(root=[])
