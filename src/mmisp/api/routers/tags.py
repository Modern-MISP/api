import re
from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import delete, func
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.tags import (
    TagCreateBody,
    TagDeleteResponse,
    TagGetResponse,
    TagResponse,
    TagSearchResponse,
    TagUpdateBody,
    TagViewResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.attribute import AttributeTag
from mmisp.db.models.event import EventTag
from mmisp.db.models.feed import Feed
from mmisp.db.models.galaxy_cluster import GalaxyCluster
from mmisp.db.models.tag import Tag
from mmisp.db.models.taxonomy import Taxonomy, TaxonomyPredicate
from mmisp.util.models import update_record
from mmisp.util.partial import partial

router = APIRouter(tags=["tags"])


@router.post(
    "/tags",
    status_code=status.HTTP_201_CREATED,
    response_model=TagResponse,
    summary="Add new tag",
)
async def add_tag(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.TAG_EDITOR]))],
    db: Annotated[Session, Depends(get_db)],
    body: TagCreateBody,
) -> TagResponse:
    """Add a new tag with given details.
    
    Input:

    - auth: Authentication details

    - db: Database session

    - body: Tag creation details

    Output:

    - TagResponse: Details of the created tag
    """
    return await _add_tag(db, body)


@router.get(
    "/tags/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=TagViewResponse,
    summary="View tag details",
)
async def view_tag(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    tag_id: Annotated[int, Path(alias="tagId")],
) -> TagViewResponse:
    """View details of a specific tag.
    
    Input:

    - auth: Authentication details

    - db: Database session

    - tag_id: ID of the tag to view

    Output:

    - TagViewResponse: Detailed information of the specified tag
    """
    return await _view_tag(db, tag_id)


@router.get(
    "/tags/search/{tagSearchTerm}",
    status_code=status.HTTP_200_OK,
    response_model=partial(TagSearchResponse),
    summary="Search tags",
)
async def search_tags(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    tag_search_term: Annotated[str, Path(alias="tagSearchTerm")],
) -> dict:
    """Search for tags using a specific search term.
    
    Input:

    - auth: Authentication details

    - db: Database session

    - tag_search_term: Search term for finding tags

    Output:

    - dict: Dictionary containing search results
    """
    return await _search_tags(db, tag_search_term)


@router.put(
    "/tags/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=TagResponse,
    summary="Edit tag",
)
async def update_tag(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    body: TagUpdateBody,
    tag_id: Annotated[int, Path(alias="tagId")],
) -> TagResponse:
    """Edit details of a specific tag.
    
    Input:

    - auth: Authentication details

    - db: Database session

    - body: Tag update details (TagUpdateBody)

    - tag_id: ID of the tag to update

    Output:

    - TagResponse: Details of the updated tag
    """
    return await _update_tag(db, body, tag_id)


@router.delete(
    "/tags/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=TagDeleteResponse,
    summary="Delete tag",
)
async def delete_tag(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    tag_id: Annotated[int, Path(alias="tagId")],
) -> TagDeleteResponse:
    """Delete a specific tag.
    
    Input:

    - auth: Authentication details

    - db: Database session

    - tag_id: ID of the tag to delete

    Output:

    - TagDeleteResponse: Confirmation of the tag deletion
    """
    return await _delete_tag(db, tag_id)


@router.get(
    "/tags",
    status_code=status.HTTP_200_OK,
    summary="Get all tags",
)
async def get_tags(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> TagGetResponse:
    """Retrieve a list of all tags.
    
    Input:

    - auth: Authentication details

    - db: Database session

    Output:

    - TagGetResponse: List of all tags
    """
    return await _get_tags(db)


# --- deprecated ---


@router.post(
    "/tags/add",
    status_code=status.HTTP_201_CREATED,
    response_model=TagResponse,
    deprecated=True,
    summary="Add new tag (Deprecated)",
)
async def add_tag_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.TAG_EDITOR]))],
    db: Annotated[Session, Depends(get_db)],
    body: TagCreateBody,
) -> TagResponse:
    """Deprecated. Add a new tag using the old route.
    
    Input:

    - auth: Authentication details

    - db: Database session

    - body: Tag creation details (TagCreateBody)

    Output:

    - TagResponse: Details of the created tag
    """
    return await _add_tag(db, body)


@router.get(
    "/tags/view/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=TagViewResponse,
    deprecated=True,
    summary="View tag details (Deprecated)",
)
async def view_tag_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    tag_id: Annotated[int, Path(alias="tagId")],
) -> TagViewResponse:
    """Deprecated. View details of a specific tag using the old route.
    
    Input:

    - auth: Authentication details

    - db: Database session

    - tag_id: ID of the tag to view

    Output:

    - TagViewResponse: Detailed information of the specified tag
    """
    return await _view_tag(db, tag_id)


@router.post(
    "/tags/edit/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=TagResponse,
    deprecated=True,
    summary="Edit tag (Deprecated)",
)
async def update_tag_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    body: TagUpdateBody,
    tag_id: Annotated[int, Path(alias="tagId")],
) -> TagResponse:
    """Deprecated. Edit a specific tag using the old route.
    
    Input:

    - auth: Authentication details

    - db: Database session

    - body: Tag update details

    - tag_id: ID of the tag to update

    Output:

    - TagResponse: Details of the updated tag
    """
    return await _update_tag(db, body, tag_id)


@router.post(
    "/tags/delete/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=TagDeleteResponse,
    deprecated=True,
    summary="Delete tag (Deprecated)",
)
async def delete_tag_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    tag_id: Annotated[int, Path(alias="tagId")],
) -> TagDeleteResponse:
    """Deprecated. Delete a specific tag using the old route.
    
    Input:

    - auth: Authentication details

    - db: Database session

    - tag_id: ID of the tag to delete

    Output:
    
    - TagDeleteResponse: Confirmation of the tag deletion
    """
    return await _delete_tag(db, tag_id)


# --- endpoint logic ---


async def _add_tag(db: Session, body: TagCreateBody) -> TagResponse:
    _check_type_hex_colour(body.colour)
    tag: Tag = Tag(**body.dict())

    result = await db.execute(select(Tag).filter(Tag.name == body.name).limit(1))
    existing_tag = result.scalars().first()
    if existing_tag:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This tag name already exists.")

    db.add(tag)
    await db.commit()

    return TagResponse.parse_obj({"Tag": tag.__dict__})


async def _view_tag(db: Session, tag_id: int) -> TagViewResponse:
    tag: Tag | None = await db.get(Tag, tag_id)

    if not tag:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tag not found.")

    result = await db.execute(select(func.count()).filter(EventTag.tag_id == tag.id))
    count = result.scalar()

    return TagViewResponse(**{**tag.__dict__, "attribute_count": 0, "count": count})


async def _search_tags(db: Session, tag_search_term: str) -> dict:
    result = await db.execute(select(Tag).filter(Tag.name.contains(tag_search_term)))
    tags: Sequence[Tag] = result.scalars().all()

    tag_datas = []
    for tag in tags:
        result = await db.execute(select(Taxonomy).filter(Taxonomy.namespace == tag.name.split(":", 1)[0]))
        taxonomies: Sequence[Taxonomy] = result.scalars().all()

        for taxonomy in taxonomies:
            result = await db.execute(select(TaxonomyPredicate).filter_by(taxonomy_id=taxonomy.id))
            taxonomy_predicates: Sequence[TaxonomyPredicate] = result.scalars().all()

            for taxonomy_predicate in taxonomy_predicates:
                tag_datas.append(
                    {
                        "Tag": tag.__dict__,
                        "Taxonomy": taxonomy.__dict__,
                        "TaxonomyPredicate": taxonomy_predicate.__dict__,
                    }
                )

    return {"response": tag_datas}


async def _update_tag(db: Session, body: TagUpdateBody, tag_id: int) -> TagResponse:
    tag: Tag | None = await db.get(Tag, tag_id)

    if not tag:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tag not found.")

    if body.name:
        result = await db.execute(select(Tag).filter(Tag.name == body.name, Tag.id != tag_id).limit(1))
        existing_tag = result.scalars().first()
        if existing_tag:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This tag name already exists.")

    if body.colour:
        _check_type_hex_colour(body.colour)

    update_record(tag, body.dict())

    await db.commit()
    await db.refresh(tag)

    return TagResponse.parse_obj({"Tag": tag.__dict__})


async def _delete_tag(db: Session, tag_id: int) -> TagDeleteResponse:
    deleted_tag: Tag | None = await db.get(Tag, tag_id)

    if not deleted_tag:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tag not found.")

    result = await db.execute(select(Feed).filter(Feed.tag_id == deleted_tag.id))
    feeds: Sequence[Feed] = result.scalars().all()

    for feed in feeds:
        feed.tag_id = 0

    result = await db.execute(select(GalaxyCluster).filter(GalaxyCluster.tag_name == deleted_tag.name))
    galaxy_clusters: Sequence[GalaxyCluster] = result.scalars().all()

    for galaxy_cluster in galaxy_clusters:
        galaxy_cluster.tag_name = ""

    await db.execute(delete(EventTag).filter(EventTag.tag_id == deleted_tag.id))
    await db.execute(delete(AttributeTag).filter(AttributeTag.tag_id == deleted_tag.id))
    await db.delete(deleted_tag)
    await db.commit()

    message = "Tag deleted."

    return TagDeleteResponse.parse_obj({"name": message, "message": message, "url": f"/tags/{tag_id}"})


async def _get_tags(db: Session) -> TagGetResponse:
    result = await db.execute(select(Tag))
    tags: Sequence[Tag] = result.scalars().all()

    return TagGetResponse(Tag=[tag.__dict__ for tag in tags])


def _check_type_hex_colour(colour: Any) -> None:
    _hex_string = re.compile(r"#[a-fA-F0-9]{6}$")
    if colour is None or not _hex_string.match(colour):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid colour code.")
