import logging
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.feeds.cache_feed_response import FeedCacheResponse
from mmisp.api_schemas.feeds.create_update_feed_body import FeedCreateAndUpdateBody
from mmisp.api_schemas.feeds.enable_disable_feed_response import FeedEnableDisableResponse
from mmisp.api_schemas.feeds.fetch_feeds_response import FeedFetchResponse
from mmisp.api_schemas.feeds.get_feed_response import FeedAttributesResponse, FeedResponse, FeedsResponse
from mmisp.api_schemas.feeds.toggle_feed_body import FeedToggleBody
from mmisp.db.database import get_db
from mmisp.db.models.feed import Feed
from mmisp.util.partial import partial
from mmisp.util.request_validations import check_existence_and_raise

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
    "/feeds",
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
    "/feeds",
    status_code=status.HTTP_200_OK,
    response_model=partial(FeedsResponse),  # type: ignore
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
    feed: Feed = Feed(
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
        db.add(feed)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Failed to add new feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    logger.info(f"New feed added: {feed.id}")

    return FeedResponse(feed={**feed.__dict__})


async def _cache_feeds(db: Session, cache_feeds_scope: str) -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint not yet supported.")

    # try:
    #     feeds_to_cache = db.query(Feed).filter(Feed.scope == cache_feeds_scope).all()  # noqa: F841
    #     #! logic to save 'feeds_to_cache' in cache (worker)
    #     message = "Feeds successfully cached" if success else "Caching failed"
    #     success = False
    #     saved = False
    #     return FeedCacheResponse(  # ? make dynamic, according to the response
    #         name="Caching Operation",
    #         message=message,
    #         url="",
    #         saved=saved,
    #         success=success,
    #     )
    # except SQLAlchemyError as e:
    #     logger.exception(f"Failed to cache feed: {e}")
    #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."


async def _fetch_from_feed(db: Session, feed_id: str) -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint not yet supported")

    # feed = db.get(Feed, feed_id)
    # if not feed:
    #     logger.error(f"Feed with id '{feed_id}' not found.")
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found.")
    # #! logic to start the pull process (worker)
    # return FeedFetchResponse(result="Pull queued for background execution.")


async def _get_feed_details(db: Session, feed_id: str) -> dict:
    feed: Feed = check_existence_and_raise(db, Feed, feed_id, "feed_id", "Feed not found.")

    return FeedResponse(feed={**feed.__dict__})


async def _update_feed(db: Session, feed_id: str, body: FeedCreateAndUpdateBody) -> dict:
    feed = check_existence_and_raise(db, Feed, feed_id, "feed_id", "Feed not found.")

    update_data = body.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(feed, key, value if not isinstance(value, Enum) else value.value)

    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Failed to update feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    logger.info(f"Feed with id '{feed.id}' updated.")
    feed_data: FeedAttributesResponse = {**feed.__dict__}

    return FeedResponse(feed=feed_data)


async def _toggle_feed(db: Session, feed_id: str, body: FeedToggleBody) -> dict:
    feed: Feed = check_existence_and_raise(db, Feed, feed_id, "feed_id", "Feed not found.")
    enable_status = body.enable

    if enable_status == feed.enabled:
        message = "Feed already " + ("enabled." if feed.enabled else "disabled.")
    else:
        feed.enabled = enable_status
        message = "Feed " + ("enabled" if enable_status else "disabled") + " successfully."

    try:
        db.commit()
        logging.info(f"Feed with id '{feed_id}': {message}.")
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Failed to toggle feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    return FeedEnableDisableResponse(name=feed.name, message=message, url=feed.url)


async def _fetch_data_from_all_feeds(db: Session) -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint not yet supported")

    # feeds = db.query(Feed).all()  # noqa: F841
    # #! logic to start the pull process
    # fetched_data = ""
    # return FeedFetchResponse(result=fetched_data)


async def _get_feeds(db: Session) -> list[dict]:
    feeds: list[Feed] = db.query(Feed).all()

    if not feeds:
        logger.info("No feeds found.")
        return FeedsResponse(feeds=[])

    return FeedsResponse(feeds=[{**feed.__dict__} for feed in feeds])


async def _enable_feed(db: Session, feed_id: str) -> dict:
    feed: Feed = check_existence_and_raise(db, Feed, feed_id, "feed_id", "Feed not found.")

    if feed.enabled:
        message = "Feed already enabled."
    else:
        feed.enabled = True
        db.commit()
        message = "Feed enabled successfully."
        logger.info(f"Feed with id '{feed_id}' enabled.")

    return FeedEnableDisableResponse(name=feed.name, message=message, url=feed.url)


async def _disable_feed(db: Session, feed_id: str) -> dict:
    feed: Feed = check_existence_and_raise(db, Feed, feed_id, "feed_id", "Feed not found.")

    if not feed.enabled:
        message = "Feed already disabled."
    else:
        feed.enabled = False
        db.commit()
        message = "Feed disabled successfully."
        logger.info(f"Feed with id '{feed_id}' disabled.")

    return FeedEnableDisableResponse(name=feed.name, message=message, url=feed.url)
