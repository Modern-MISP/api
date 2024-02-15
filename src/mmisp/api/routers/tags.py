import logging
import re
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.tags.create_tag_body import TagCreateBody
from mmisp.api_schemas.tags.delete_tag_response import TagDeleteResponse
from mmisp.api_schemas.tags.get_tag_response import TagAttributesResponse, TagGetResponse
from mmisp.api_schemas.tags.search_tags_response import TagCombinedModel, TagSearchResponse, TaxonomyPredicateResponse
from mmisp.api_schemas.tags.update_tag_body import TagUpdateBody
from mmisp.api_schemas.taxonomies.get_taxonomy_out import TaxonomyView
from mmisp.db.database import get_db
from mmisp.db.models.attribute import AttributeTag
from mmisp.db.models.feed import Feed
from mmisp.db.models.tag import Tag
from mmisp.db.models.taxonomy import Taxonomy, TaxonomyPredicate
from mmisp.util.models import update_record
from mmisp.util.partial import partial
from mmisp.util.request_validations import check_existence_and_raise

router = APIRouter(tags=["tags"])

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


@router.post(
    "/tags",
    status_code=status.HTTP_201_CREATED,
    response_model=partial(TagAttributesResponse),
    summary="Add new tag",
    description="Add a new tag with given details.",
)
async def add_tag(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, Permission.FULL))],
    db: Annotated[Session, Depends(get_db)],
    body: TagCreateBody,
) -> dict:
    return await _add_tag(db, body)


@router.get(
    "/tags/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(TagAttributesResponse),
    summary="View tag details",
    description="View details of a specific tag.",
)
async def view_tag(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, Permission.FULL))],
    db: Annotated[Session, Depends(get_db)],
    tag_id: str = Path(..., alias="tagId"),
) -> dict:
    return await _view_tag(db, tag_id)


@router.get(
    "/tags/search/{tagSearchTerm}",
    status_code=status.HTTP_200_OK,
    response_model=partial(TagSearchResponse),
    summary="Search tags",
    description="Search for tags using a specific search term.",
)
async def search_tags(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, Permission.FULL))],
    db: Annotated[Session, Depends(get_db)],
    tag_search_term: str = Path(..., alias="tagSearchTerm"),
) -> dict:
    return await _search_tags(db, tag_search_term)


@router.put(
    "/tags/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(TagAttributesResponse),
    summary="Edit tag",
    description="Edit details of a specific tag.",
)
async def update_tag(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, Permission.FULL))],
    db: Annotated[Session, Depends(get_db)],
    body: TagUpdateBody,
    tag_id: str = Path(..., alias="tagId"),
) -> dict:
    return await _update_tag(db, body, tag_id)


@router.delete(
    "/tags/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=TagDeleteResponse,
    summary="Delete tag",
    description="Delete a specific tag.",
)
async def delete_tag(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, Permission.FULL))],
    db: Annotated[Session, Depends(get_db)],
    tag_id: str = Path(..., alias="tagId"),
) -> dict:
    return await _delete_tag(db, tag_id)


@router.get(
    "/tags",
    status_code=status.HTTP_200_OK,
    response_model=partial(TagGetResponse),
    summary="Get all tags",
    description="Retrieve a list of all tags.",
)
async def get_tags(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, Permission.FULL))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _get_tags(db)


@router.post(
    "/tags/add",
    status_code=status.HTTP_201_CREATED,
    response_model=partial(TagAttributesResponse),
    deprecated=True,
    summary="Add new tag (Deprecated)",
    description="Deprecated. Add a new tag using the old route.",
)
async def add_tag_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, Permission.FULL))],
    db: Annotated[Session, Depends(get_db)],
    body: TagCreateBody,
) -> dict:
    return await _add_tag(db, body)


@router.get(
    "/tags/view/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(TagAttributesResponse),
    deprecated=True,
    summary="View tag details (Deprecated)",
    description="Deprecated. View details of a specific tag using the old route.",
)
async def view_tag_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, Permission.FULL))],
    db: Annotated[Session, Depends(get_db)],
    tag_id: str = Path(..., alias="tagId"),
) -> dict:
    return await _view_tag(db, tag_id)


@router.post(
    "/tags/edit/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(TagAttributesResponse),
    deprecated=True,
    summary="Edit tag (Deprecated)",
    description="Deprecated. Edit a specific tag using the old route.",
)
async def update_tag_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, Permission.FULL))],
    db: Annotated[Session, Depends(get_db)],
    body: TagCreateBody,
    tag_id: str = Path(..., alias="tagId"),
) -> dict:
    return await _update_tag(db, body, tag_id)


@router.post(
    "/tags/delete/{tagId}",
    status_code=status.HTTP_200_OK,
    response_model=TagDeleteResponse,
    deprecated=True,
    summary="Delete tag (Deprecated)",
    description="Deprecated. Delete a specific tag using the old route.",
)
async def delete_tag_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, Permission.FULL))],
    db: Annotated[Session, Depends(get_db)],
    tag_id: str = Path(..., alias="tagId"),
) -> dict:
    return await _delete_tag(db, tag_id)


# --- endpoint logic ---
async def _add_tag(
    db: Session,
    body: TagCreateBody,
) -> dict:
    _check_type_hex_color(body.colour)
    tag: Tag = Tag(**body.dict())

    try:
        db.add(tag)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Failed to add new tag: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    logger.info(f"New tag added: {tag.id}")

    return tag.__dict__


async def _view_tag(
    db: Session,
    tag_id: str,
) -> dict:
    tag: Tag = check_existence_and_raise(db, Tag, tag_id, "id", "Tag not found.")

    return tag.__dict__


async def _search_tags(
    db: Session,
    tag_search_term: str,
) -> dict:
    regex_tag_search_term = "%" + tag_search_term + "%"

    # tags = db.query(Tag).filter_by(Tag.name.like(regex_tag_search_term)).all()
    tags = db.query(Tag).filter(Tag.name.contains(regex_tag_search_term)).all()

    tag_datas = []
    for tag in tags:
        taxonomies = db.query(Taxonomy).filter_by(tag=tag.name).all()
        for taxonomy in taxonomies:
            taxonomy_predicate = db.query(TaxonomyPredicate).filter_by(taxonomy_id=taxonomy.id).first()
            tag_datas.append(
                TagCombinedModel(
                    Tag(tag=tag.__dict__),
                    TaxonomyView(taxonomy=taxonomy.__dict__),
                    TaxonomyPredicateResponse(taxonomy_predicate=taxonomy_predicate.__dict__),
                )
            )

    return TagSearchResponse(root=[tag_data.__dict__ for tag_data in tag_datas])


async def _update_tag(
    db: Session,
    body: TagCreateBody,
    tag_id: str,
) -> dict:
    tag: Tag = check_existence_and_raise(db, Tag, tag_id, "id", "Tag not found.")
    _check_type_hex_color(body.colour)
    update_data = body.dict()

    if db.query(Tag).filter(Tag.name == body.name).first() is not None:
        logger.info(f"name is: {body.name}")
        raise HTTPException(400)

    update_record(tag, update_data)

    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Failed to update tag: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    db.refresh(tag)

    logger.info(f"Tag with id '{tag.id}' updated.")

    return tag.__dict__


async def _delete_tag(
    db: Session,
    tag_id: str,
) -> dict:
    deleted_tag = check_existence_and_raise(db, Tag, tag_id, "tag_id", "Tag not found.")

    feeds = db.query(Feed).filter(Feed.tag_id == deleted_tag.id).all()
    for feed in feeds:
        feed.tag_id = None
    attribute_tags = db.query(AttributeTag).filter(AttributeTag.tag_id == deleted_tag.id).all()
    for attribute_tag in attribute_tags:
        attribute_tag.tag_id = None
    taxonomies = db.query(Taxonomy).filter(Taxonomy.tag == deleted_tag.name).all()
    for taxonomy in taxonomies:
        taxonomy.tag_name = None

    db.delete(deleted_tag)
    try:
        db.commit()
        logger.info(f"Deleted tag with id '{tag_id}'.")
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to delete tag with id '{tag_id}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )
    message = "Tag deleted."

    return TagDeleteResponse(name=message, message=message, url=f"/tags/{tag_id}")


async def _get_tags(db: Session) -> dict:
    tags: list[Tag] | None = db.query(Tag).all()

    if not tags:
        logger.error("No tags found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tags found.")

    return TagGetResponse(tag=[tag.__dict__ for tag in tags])


def _check_type_hex_color(colour: Any) -> None:
    _hex_string = re.compile(r"#[a-fA-F0-9]{6}$")
    if colour is None or not _hex_string.match(colour):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid colour code.")
