from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.feeds import (
    FeedCacheResponse,
    FeedCreateBody,
    FeedEnableDisableResponse,
    FeedFetchResponse,
    FeedResponse,
    FeedToggleBody,
    FeedUpdateBody,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.feed import Feed
from mmisp.util.models import update_record

router = APIRouter(tags=["feeds"])


@router.post(
    "/feeds",
    status_code=status.HTTP_201_CREATED,
    response_model=FeedResponse,
    summary="Add new feed",
    description="Add a new feed with given details.",
)
async def add_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    body: FeedCreateBody,
) -> FeedResponse:
    return await _add_feed(db, body)


@router.post(  # @worker: also change 'status_code' and 'description'
    "/feeds/cache_feeds/{cacheFeedsScope}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=FeedCacheResponse,
    summary="Cache feeds",
    description="Cache feeds based on a specific scope. NOT YET AVAILABLE!",
)
async def cache_feeds(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    cache_feeds_scope: Annotated[str, Path(alias="cacheFeedsScope")],
) -> FeedCacheResponse:
    return await _cache_feeds(db, cache_feeds_scope)


@router.get(  # @worker: also change 'status_code' and 'description'
    "/feeds/fetch_from_feed/{feedId}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=FeedFetchResponse,
    summary="Fetch from feed",
    description="Fetch data from a specific feed by its ID. NOT YET AVAILABLE!",
)
async def fetch_from_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
) -> FeedFetchResponse:
    return await _fetch_from_feed(db, feed_id)


@router.get(
    "/feeds/{feedId}",
    status_code=status.HTTP_200_OK,
    response_model=FeedResponse,
    summary="Get feed details",
    description="Retrieve details of a specific feed by its ID.",
)
async def get_feed_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
) -> FeedResponse:
    return await _get_feed_details(db, feed_id)


@router.put(
    "/feeds/{feedId}",
    status_code=status.HTTP_200_OK,
    response_model=FeedResponse,
    summary="Update feed",
    description="Update an existing feed by its ID.",
)
async def update_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
    body: FeedUpdateBody,
) -> FeedResponse:
    return await _update_feed(db, feed_id, body)


@router.patch(
    "/feeds/{feedId}",
    status_code=status.HTTP_200_OK,
    response_model=FeedEnableDisableResponse,
    summary="Toggle feed status",
    description="Toggle the status of a feed between enabled and disabled.",
)
async def toggle_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
    body: FeedToggleBody,
) -> FeedEnableDisableResponse:
    return await _toggle_feed(db, feed_id, body)


@router.get(  # @worker: also change 'status_code' and 'description'
    "/feeds/fetch_from_all_feeds",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=FeedFetchResponse,
    summary="Fetch from all feeds",
    description="Fetch data from all available feeds. NOT YET AVAILABLE!",
)
async def fetch_data_from_all_feeds(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> FeedFetchResponse:
    return await _fetch_data_from_all_feeds(db)


@router.get(
    "/feeds",
    status_code=status.HTTP_200_OK,
    response_model=list[FeedResponse],
    summary="Get all feeds",
    description="Retrieve a list of all feeds.",
)
async def get_feeds(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[FeedResponse]:
    return await _get_feeds(db)


# --- deprecated ---


@router.post(
    "/feeds/add",
    deprecated=True,
    status_code=status.HTTP_201_CREATED,
    response_model=FeedResponse,
    summary="Add new feed (Deprecated)",
    description="Deprecated. Add a new feed with given details using the old route.",
)
async def add_feed_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    body: FeedCreateBody,
) -> FeedResponse:
    return await _add_feed(db, body)


@router.post(
    "/feeds/enable/{feedId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=FeedEnableDisableResponse,
    summary="Enable feed (Deprecated)",
    description="Deprecated. Enable a specific feed by its ID using the old route.",
)
async def enable_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
) -> FeedEnableDisableResponse:
    return await _enable_feed(db, feed_id)


@router.post(
    "/feeds/disable/{feedId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=FeedEnableDisableResponse,
    summary="Disable feed (Deprecated)",
    description="Deprecated. Disable a specific feed by its ID using the old route.",
)
async def disable_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
) -> FeedEnableDisableResponse:
    return await _disable_feed(db, feed_id)


@router.post(  # @worker: also change 'status_code' and 'description'
    "/feeds/cacheFeeds/{cacheFeedsScope}",
    deprecated=True,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=FeedCacheResponse,
    summary="Cache feeds",
    description="Cache feeds based on a specific scope.",
)
async def cache_feeds_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    cache_feeds_scope: Annotated[str, Path(alias="cacheFeedsScope")],
) -> FeedCacheResponse:
    return await _cache_feeds(db, cache_feeds_scope)


@router.post(  # @worker: also change 'status_code' and 'description'
    "/feeds/fetchFromFeed/{feedId}",
    deprecated=True,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=FeedFetchResponse,
    summary="Fetch from feed (Deprecated)",
    description="Deprecated. Fetch data from a specific feed by its ID using the old route.",
)
async def fetch_from_feed_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
) -> FeedFetchResponse:
    return await _fetch_from_feed(db, feed_id)


@router.post(  # @worker: also change 'status_code' and 'description'
    "/feeds/fetchFromAllFeeds",
    deprecated=True,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=FeedFetchResponse,
    summary="Fetch from all feeds (Deprecated)",
    description="Deprecated. Fetch data from all available feeds using the old route.",
)
async def fetch_data_from_all_feeds_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> FeedFetchResponse:
    return await _fetch_data_from_all_feeds(db)


@router.get(
    "/feeds/view/{feedId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=FeedResponse,
    summary="Get feed details (Deprecated)",
    description="Deprecated. Retrieve details of a specific feed by its ID using the old route.",
)
async def get_feed_details_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
) -> FeedResponse:
    return await _get_feed_details(db, feed_id)


@router.put(
    "/feeds/edit/{feedId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=FeedResponse,
    summary="Update feed (Deprecated)",
    description="Deprecated. Update an existing feed by its ID using the old route.",
)
async def update_feed_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
    body: FeedUpdateBody,
) -> FeedResponse:
    return await _update_feed(db, feed_id, body)


# --- endpoint logic ---


async def _add_feed(db: Session, body: FeedCreateBody) -> FeedResponse:
    feed: Feed = Feed(**body.dict())

    db.add(feed)
    await db.commit()
    await db.refresh(feed)

    return FeedResponse(Feed=feed.__dict__)


async def _cache_feeds(db: Session, cache_feeds_scope: str) -> FeedCacheResponse:
    # logic to save 'feeds_to_cache' in cache (worker)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint not yet supported.")


async def _fetch_from_feed(db: Session, feed_id: int) -> FeedFetchResponse:
    # logic to start the pull process (worker)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint not yet supported.")


async def _get_feed_details(db: Session, feed_id: int) -> FeedResponse:
    feed: Feed | None = await db.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    return FeedResponse(Feed=feed.__dict__)


async def _update_feed(db: Session, feed_id: int, body: FeedUpdateBody) -> FeedResponse:
    feed: Feed | None = await db.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    update_record(feed, body.dict())

    await db.commit()
    await db.refresh(feed)

    return FeedResponse(Feed=feed.__dict__)


async def _toggle_feed(db: Session, feed_id: int, body: FeedToggleBody) -> FeedEnableDisableResponse:
    feed: Feed | None = await db.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    enable_status: bool = body.enable

    target_status = "enabled" if body.enable else "disabled"
    message = f"Feed already {target_status}."

    if enable_status != feed.enabled:
        feed.enabled = enable_status
        message = f"Feed {target_status} successfully."

    await db.commit()

    return FeedEnableDisableResponse(name=feed.name, message=message, url=feed.url)


async def _fetch_data_from_all_feeds(db: Session) -> FeedFetchResponse:
    # logic to start the pull process for all feeds
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint not yet supported.")


async def _get_feeds(db: Session) -> list[FeedResponse]:
    result = await db.execute(select(Feed))
    feeds: Sequence[Feed] = result.scalars().all()

    return [FeedResponse(Feed=feed.__dict__) for feed in feeds]


async def _enable_feed(db: Session, feed_id: int) -> FeedEnableDisableResponse:
    feed: Feed | None = await db.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    if feed.enabled:
        message = "Feed already enabled."
    else:
        feed.enabled = True
        await db.commit()
        message = "Feed enabled successfully."

    return FeedEnableDisableResponse(name=feed.name, message=message, url=feed.url)


async def _disable_feed(db: Session, feed_id: int) -> FeedEnableDisableResponse:
    feed: Feed | None = await db.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    if not feed.enabled:
        message = "Feed already disabled."
    else:
        feed.enabled = False
        await db.commit()
        message = "Feed disabled successfully."

    return FeedEnableDisableResponse(name=feed.name, message=message, url=feed.url)
