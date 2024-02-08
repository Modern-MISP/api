import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.feeds.cache_feed_response import FeedCacheResponse
from mmisp.api_schemas.feeds.create_update_feed_body import FeedCreateAndUpdateBody
from mmisp.api_schemas.feeds.enable_disable_feed_response import FeedEnableDisableResponse
from mmisp.api_schemas.feeds.fetch_feeds_response import FeedFetchResponse
from mmisp.api_schemas.feeds.get_feed_response import FeedAttributesResponse, FeedResponse
from mmisp.api_schemas.feeds.toggle_feed_body import FeedToggleBody
from mmisp.db.database import get_db
from mmisp.db.models.feed import Feed
from mmisp.util.partial import partial

router = APIRouter(tags=["feeds"])
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


# sorted according to CRUD


@router.post(
    "/feeds/",
    status_code=status.HTTP_201_CREATED,
    response_model=partial(FeedResponse),
    summary="Add new feed",
    description="Add a new feed with given details.",
)
async def add_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    body: FeedCreateAndUpdateBody,
) -> dict:
    return await _add_feed(db, body)


@router.post(  #! @worker: also change 'status_code' and 'description'
    "/feeds/cache_feeds/{cacheFeedsScope}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(FeedCacheResponse),
    summary="Cache feeds",
    description="Cache feeds based on a specific scope. NOT YET AVAILABLE!",
)
async def cache_feeds(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADMIN, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    cache_feeds_scope: Annotated[str, Path(..., alias="cacheFeedsScope")],
) -> dict:
    return await _cache_feeds(db, cache_feeds_scope)


@router.get(  #! @worker: also change 'status_code' and 'description'
    "/feeds/fetch_from_feed/{feedId}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(FeedFetchResponse),
    summary="Fetch from feed",
    description="Fetch data from a specific feed by its ID. NOT YET AVAILABLE!",
)
async def fetch_from_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SYNC]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[str, Path(..., alias="feedId")],
) -> dict:
    return await _fetch_from_feed(db, feed_id)


@router.get(
    "/feeds/{feedId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(FeedResponse),
    summary="Get feed details",
    description="Retrieve details of a specific feed by its ID.",
)
async def get_feed_details(
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[str, Path(..., alias="feedId")],
) -> dict:
    return await _get_feed_details(db, feed_id)


@router.put(
    "/feeds/{feedId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(FeedResponse),
    summary="Update feed",
    description="Update an existing feed by its ID.",
)
async def update_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[str, Path(..., alias="feedId")],
    body: FeedCreateAndUpdateBody,
) -> dict:
    return await _update_feed(db, feed_id, body)


@router.patch(
    "/feeds/{feedId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(FeedEnableDisableResponse),
    summary="Toggle feed status",
    description="Toggle the status of a feed between enabled and disabled.",
)
async def toggle_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[str, Path(..., alias="feedId")],
    body: FeedToggleBody,
) -> dict:
    return await _toggle_feed(db, feed_id, body)


@router.get(  #! @worker: also change 'status_code' and 'description'
    "/feeds/fetch_from_all_feeds",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(FeedFetchResponse),
    summary="Fetch from all feeds",
    description="Fetch data from all available feeds. NOT YET AVAILABLE!",
)
async def fetch_data_from_all_feeds(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SYNC]))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _fetch_data_from_all_feeds(db)


@router.get(
    "/feeds/",
    status_code=status.HTTP_200_OK,
    response_model=list[partial(FeedResponse)],  # type: ignore
    summary="Get all feeds",
    description="Retrieve a list of all feeds.",
)
async def get_feeds(db: Annotated[Session, Depends(get_db)]) -> list[dict]:
    return await _get_feeds(db)


# --- deprecated ---


@router.post(
    "/feeds/add",
    deprecated=True,
    status_code=status.HTTP_201_CREATED,
    response_model=partial(FeedResponse),
    summary="Add new feed (Deprecated)",
    description="Deprecated. Add a new feed with given details using the old route.",
)
async def add_feed_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Annotated[Session, Depends(get_db)],
    body: FeedCreateAndUpdateBody,
) -> dict:
    return await _add_feed(db, body)


@router.post(
    "/feeds/enable/{feedId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(FeedEnableDisableResponse),
    summary="Enable feed (Deprecated)",
    description="Deprecated. Enable a specific feed by its ID using the old route.",
)
async def enable_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[str, Path(..., alias="feedId")],
) -> dict:
    return await _enable_feed(db, feed_id)


@router.post(
    "/feeds/disable/{feedId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(FeedEnableDisableResponse),
    summary="Disable feed (Deprecated)",
    description="Deprecated. Disable a specific feed by its ID using the old route.",
)
async def disable_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[str, Path(..., alias="feedId")],
) -> dict:
    return await _disable_feed(db, feed_id)


@router.post(  #! @worker: also change 'status_code' and 'description'
    "/feeds/cacheFeeds/{cacheFeedsScope}",
    deprecated=True,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(FeedCacheResponse),
    summary="Cache feeds",
    description="Cache feeds based on a specific scope.",
)
async def cache_feeds_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADMIN, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    cache_feeds_scope: Annotated[str, Path(..., alias="cacheFeedsScope")],
) -> dict:
    return await _cache_feeds(db, cache_feeds_scope)


@router.post(  #! @worker: also change 'status_code' and 'description'
    "/feeds/fetchFromFeed/{feedId}",
    deprecated=True,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(FeedFetchResponse),
    summary="Fetch from feed (Deprecated)",
    description="Deprecated. Fetch data from a specific feed by its ID using the old route.",
)
async def fetch_from_feed_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SYNC]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[str, Path(..., alias="feedId")],
) -> dict:
    return await _fetch_from_feed(db, feed_id)


@router.post(  #! @worker: also change 'status_code' and 'description'
    "/feeds/fetchFromAllFeeds",
    deprecated=True,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(FeedFetchResponse),
    summary="Fetch from all feeds (Deprecated)",
    description="Deprecated. Fetch data from all available feeds using the old route.",
)
async def fetch_data_from_all_feeds_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SYNC]))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _fetch_data_from_all_feeds(db)


@router.get(
    "/feeds/view/{feedId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(FeedResponse),
    summary="Get feed details (Deprecated)",
    description="Deprecated. Retrieve details of a specific feed by its ID using the old route.",
)
async def get_feed_details_depr(
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[str, Path(..., alias="feedId")],
) -> dict:
    return await _get_feed_details(db, feed_id)


@router.put(
    "/feeds/edit/{feedId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(FeedResponse),
    summary="Update feed (Deprecated)",
    description="Deprecated. Update an existing feed by its ID using the old route.",
)
async def update_feed_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[str, Path(..., alias="feedId")],
    body: FeedCreateAndUpdateBody,
) -> dict:
    return await _update_feed(db, feed_id, body)


# --- endpoint logic ---


async def _add_feed(db: Session, body: FeedCreateAndUpdateBody) -> dict:
    if not body.name:
        logger.error("Feed creation failed: field 'name' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'name' is required.")
    if not body.provider:
        logger.error("Feed creation failed: field 'provider' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'provider' is required.")
    if not body.url:
        logger.error("Feed creation failed: field 'url' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'url' is required.")

    new_feed: Feed = Feed(
        **{
            **body.dict(),
            "distribution": int(body.distribution) if body.distribution is not None else None,
            "sharing_group_id": int(body.sharing_group_id) if body.sharing_group_id is not None else None,
            "tag_id": int(body.tag_id) if body.tag_id is not None else None,
            "event_id": int(body.event_id) if body.event_id is not None else None,
            "orgc_id": int(body.orgc_id) if body.orgc_id is not None else None,
        }
    )

    try:
        db.add(new_feed)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to add new feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    db.refresh(new_feed)
    logger.info(f"New feed added: {new_feed.id}")

    feed_data: FeedAttributesResponse = _prepare_response(new_feed)

    return FeedResponse(feed=[feed_data])


async def _cache_feeds(db: Session, cache_feeds_scope: str) -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="ENDPOINT NOT YET SUPPORTED!")

    # try:
    #     feeds_to_cache = db.query(Feed).filter(Feed.scope == cache_feeds_scope).all()  # noqa: F841
    #     #! logic to save 'feeds_to_cache' in cache (worker)
    #     # message = "Feeds successfully cached" if success else "Caching failed"
    #     message = "ENDPOINT NOT YET SUPPORTED"
    #     success = False
    #     saved = False
    #     return FeedCacheResponse(  # ? make dynamic, according to the response
    #         name="Caching Operation",
    #         message=message,
    #         url="",
    #         saved=saved,
    #         success=success,
    #     )
    # except Exception as e:
    #     logger.exception(f"Failed to cache feed: {e}")
    #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."


async def _fetch_from_feed(db: Session, feed_id: str) -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="ENDPOINT NOT YET SUPPORTED!")

    # feed = db.get(Feed, feed_id)
    # if not feed:
    #     logger.error(f"Feed with id '{feed_id}' not found.")
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found.")
    # #! logic to start the pull process (worker)
    # return FeedFetchResponse(result="Pull queued for background execution.")


async def _get_feed_details(db: Session, feed_id: str) -> dict:
    feed: Feed | None = db.get(Feed, feed_id)

    if not feed:
        logger.error(f"Feed with id '{feed_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    feed_data: FeedAttributesResponse = _prepare_response(feed)

    return FeedResponse(feed=[feed_data])


async def _update_feed(db: Session, feed_id: str, body: FeedCreateAndUpdateBody) -> dict:
    feed: Feed | None = db.get(Feed, feed_id)

    if not feed:
        logger.error(f"Feed with id '{feed_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    if not body.name:
        logger.error("Updating feed failed: field 'name' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'name' is required.")
    if not body.provider:
        logger.error("Updating feed failed: field 'provider' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'provider' is required.")
    if not body.url:
        logger.error("Updating feed failed: field 'url' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'url' is required.")

    updated_feed: Feed = Feed(
        **{
            **body.dict(),
            "distribution": int(body.distribution) if body.distribution is not None else None,
            "sharing_group_id": int(body.sharing_group_id) if body.sharing_group_id is not None else None,
            "tag_id": int(body.tag_id) if body.tag_id is not None else None,
            "event_id": int(body.event_id) if body.event_id is not None else None,
            "orgc_id": int(body.orgc_id) if body.orgc_id is not None else None,
        }
    )

    try:
        db.add(updated_feed)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to update feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    db.refresh(updated_feed)
    logger.info(f"Feed with id '{updated_feed.id}' updated.")

    feed_data: FeedAttributesResponse = _prepare_response(updated_feed)

    return FeedResponse(feed=[feed_data])


async def _toggle_feed(db: Session, feed_id: str, body: FeedToggleBody) -> dict:
    feed: Feed | None = db.get(Feed, feed_id)
    message: str = ""

    if not feed:
        logger.error(f"Feed with id '{feed_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    if not str(body.enable):
        logger.error("Toggle feed failed: field 'enable' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'enable' is required.")

    if int(body.enable) and not feed.enabled:
        feed.enabled = True
        message = "Feed enabled successfully."
    elif not int(body.enable) and feed.enabled:
        feed.enabled = False
        message = "Feed disabled successfully."
    elif int(body.enable) and feed.enabled:
        message = "Feed already enabled."
    elif not int(body.enable) and not feed.enabled:
        message = "Feed already disabled."

    try:
        db.commit()
        logging.info(f"Feed with id '{feed_id}': {message}.")
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to toggle feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    return FeedEnableDisableResponse(name=feed.name, message=message, url=feed.url)


async def _fetch_data_from_all_feeds(db: Session) -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="ENDPOINT NOT YET SUPPORTED!")

    # feeds = db.query(Feed).all()  # noqa: F841
    # #! logic to start the pull process
    # fetched_data = ""
    # return FeedFetchResponse(result=fetched_data)


async def _get_feeds(db: Session) -> list[dict]:
    feeds: list[Feed] | None = db.query(Feed).all()

    if not feeds:
        logger.error("No feeds found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No feeds found.")

    feed_responses: list[FeedAttributesResponse] = [_prepare_response(feed) for feed in feeds]

    return [FeedResponse(feed=feed_responses)]


async def _enable_feed(db: Session, feed_id: str) -> dict:
    message: str = ""

    try:
        int(feed_id)
    except ValueError:
        logger.error(f"Used a invalid feed id: '{feed_id}'")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid feed ID.")

    feed: Feed | None = db.get(Feed, feed_id)
    if not feed:
        logger.error(f"Feed with id '{feed_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    if not feed.enabled:
        feed.enabled = True
        message = "Feed enabled successfully."
    elif feed.enabled:
        message = "Feed already enabled."

    feed.enabled = True

    try:
        db.commit()
        logger.info(f"Feed with id '{feed_id}' enabled.")
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to enable feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    return FeedEnableDisableResponse(name=feed.name, message=message, url=feed.url)


async def _disable_feed(db: Session, feed_id: str) -> dict:
    message: str = ""

    try:
        int(feed_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid feed ID.")

    feed: Feed | None = db.get(Feed, feed_id)
    if not feed:
        logger.error(f"Feed with id '{feed_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    if feed.enabled:
        feed.enabled = False
        message = "Feed disabled successfully."
    elif not feed.enabled:
        message = "Feed already disabled."

    try:
        db.commit()
        logger.info(f"Feed with id '{feed_id}' disabled.")
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to disable feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    return FeedEnableDisableResponse(name=str(feed.name), message=message, url=str(feed.url))


def _prepare_response(feed: Feed) -> FeedAttributesResponse:
    feed_dict: dict[str, Any] = feed.__dict__.copy()

    fields_to_convert = ["distribution", "sharing_group_id", "tag_id", "event_id", "orgc_id"]
    for field in fields_to_convert:
        if feed_dict.get(field) is not None:
            feed_dict[field] = str(feed_dict[field])

    return FeedAttributesResponse(**feed_dict)
