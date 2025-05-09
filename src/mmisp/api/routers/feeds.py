from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, authorize
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
from mmisp.lib.logger import alog
from mmisp.lib.permissions import Permission

router = APIRouter(tags=["feeds"])


@router.get(
    "/feeds/index",
    status_code=status.HTTP_200_OK,
)
@router.get(
    "/feeds",
    status_code=status.HTTP_200_OK,
)
@alog
async def get_feeds(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[FeedResponse]:
    """Retrieve a list of all feeds.

    Args:
      auth: the user's authentification status
      db: the current database

    Returns:
      all feeds as a list
    """
    return await _get_feeds(db)


@router.post(
    "/feeds",
    status_code=status.HTTP_201_CREATED,
)
@alog
async def add_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    body: FeedCreateBody,
) -> FeedResponse:
    """Add a new feed with given details.

    Args:
      auth: the user's authentification status
      db: the current database
      body: the request body

    Returns:
      the new feed
    """
    return await _add_feed(db, body)


@router.post(  # @worker: also change 'status_code'
    "/feeds/cache_feeds/{cacheFeedsScope}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
@alog
async def cache_feeds(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    cache_feeds_scope: Annotated[str, Path(alias="cacheFeedsScope")],
) -> FeedCacheResponse:
    """Cache feeds based on a specific scope. NOT YET AVAILABLE!

    Args:
      auth: the user's authentification status
      db: the current database
      cache_feeds_scope: the cache feeds scope

    Returns:
      the cache feeds
    """
    return await _cache_feeds(db, cache_feeds_scope)


@router.get(  # @worker: also change 'status_code'
    "/feeds/fetch_from_feed/{feedId}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
@alog
async def fetch_from_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
) -> FeedFetchResponse:
    """Fetch data from a specific feed by its ID. NOT YET AVAILABLE!

    Args:
      auth: the user's authentification status
      db: the current database
      feed_id: the feed id

    Returns:
      the fetched feed data
    """
    return await _fetch_from_feed(db, feed_id)


@router.get(
    "/feeds/{feedId}",
    status_code=status.HTTP_200_OK,
)
@alog
async def get_feed_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
) -> FeedResponse:
    """Retrieve details of a specific feed by its ID.

    Args:
      auth: the user's authentification status
      db: the current database
      feed_id: the feed id

    Returns:
      the details of a feed
    """
    return await _get_feed_details(db, feed_id)


@router.put(
    "/feeds/{feedId}",
    status_code=status.HTTP_200_OK,
)
@alog
async def update_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
    body: FeedUpdateBody,
) -> FeedResponse:
    """Update an existing feed by its ID.

    Args:
      auth: the user's authentification status
      db: the current database
      feed_id: the feed id
      body: the request body

    Returns:
      the updated feed
    """
    return await _update_feed(db, feed_id, body)


@router.patch(
    "/feeds/{feedId}",
    status_code=status.HTTP_200_OK,
)
@alog
async def toggle_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
    body: FeedToggleBody,
) -> FeedEnableDisableResponse:
    """Toggle the status of a feed between enabled and disabled.


    Args:
      auth: the user's authentification status
      db: the current database
      feed_id: the feed id
      body: the request body

    Returns:
      the new status of the feed
    """
    return await _toggle_feed(db, feed_id, body)


@router.get(  # @worker: also change 'status_code'
    "/feeds/fetch_from_all_feeds",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
@alog
async def fetch_data_from_all_feeds(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> FeedFetchResponse:
    """Fetch data from all available feeds. NOT YET AVAILABLE!

    Args:
      auth: the user's authentification status
      db: the current database

    Returns:
      the fetched data of all available feeds
    """
    return await _fetch_data_from_all_feeds(db)


# --- deprecated ---


@router.post(
    "/feeds/add",
    deprecated=True,
    status_code=status.HTTP_201_CREATED,
)
@alog
async def add_feed_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    body: FeedCreateBody,
) -> FeedResponse:
    """Deprecated. Add a new feed with given details using the old route.

    Args:
      auth: the user's authentification status
      db: the current database
      body: the request body

    Returns:
      the added feed
    """
    return await _add_feed(db, body)


@router.post(
    "/feeds/enable/{feedId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
)
@alog
async def enable_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
) -> FeedEnableDisableResponse:
    """Deprecated. Enable a specific feed by its ID using the old route.

    Args:
      auth: user's authentification status
      db: current database
      feed_id: feed id

    Returns:
      the the enabled feed
    """
    return await _enable_feed(db, feed_id)


@router.post(
    "/feeds/disable/{feedId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
)
@alog
async def disable_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
) -> FeedEnableDisableResponse:
    """Deprecated. Disable a specific feed by its ID using the old route.

    Args:
      the user's authentification status
      the current database
      the feed id

    Returns:
      the disabled feed
    """
    return await _disable_feed(db, feed_id)


@router.post(  # @worker: also change 'status_code'
    "/feeds/cacheFeeds/{cacheFeedsScope}",
    deprecated=True,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
@alog
async def cache_feeds_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    cache_feeds_scope: Annotated[str, Path(alias="cacheFeedsScope")],
) -> FeedCacheResponse:
    """Cache feeds based on a specific scope.

    Args:
      auth: the user's authentification status
      db: the current database
      cache_feeds_scope: the cache feeds scope

    Returns:
      the feed cache
    """
    return await _cache_feeds(db, cache_feeds_scope)


@router.post(  # @worker: also change 'status_code'
    "/feeds/fetchFromFeed/{feedId}",
    deprecated=True,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Fetch from feed (Deprecated)",
)
@alog
async def fetch_from_feed_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
) -> FeedFetchResponse:
    """Deprecated. Fetch data from a specific feed by its ID using the old route.

    Args:
      auth: the user's authentification status
      db: the current database
      feed_id: the feed id

    Returns:
     the fetched feed data
    """
    return await _fetch_from_feed(db, feed_id)


@router.post(  # @worker: also change 'status_code'
    "/feeds/fetchFromAllFeeds",
    deprecated=True,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
@alog
async def fetch_data_from_all_feeds_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> FeedFetchResponse:
    """Deprecated. Fetch data from all available feeds using the old route.

    Args:
      auth: the user's authentification status
      db: the current database

    Returns:
      the fetched data of all feeds
    """
    return await _fetch_data_from_all_feeds(db)


@router.get(
    "/feeds/view/{feedId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
)
@alog
async def get_feed_details_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
) -> FeedResponse:
    """Deprecated. Retrieve details of a specific feed by its ID using the old route.

    Args:
      auth: the user's authentification status
      db: the current database
      feed_id: the feed id

    Returns:
      the details of the feed
    """
    return await _get_feed_details(db, feed_id)


@router.put(
    "/feeds/edit/{feedId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
)
@alog
async def update_feed_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    feed_id: Annotated[int, Path(alias="feedId")],
    body: FeedUpdateBody,
) -> FeedResponse:
    """Deprecated. Update an existing feed by its ID using the old route.


    Args:
      auth: the user's authentification status
      db: the current database
      feed_id: the feed id
      body: the request body

    Returns:
      the updated feed
    """
    return await _update_feed(db, feed_id, body)


# --- endpoint logic ---


@alog
async def _add_feed(db: Session, body: FeedCreateBody) -> FeedResponse:
    feed: Feed = Feed(**body.model_dump())

    db.add(feed)
    await db.flush()
    await db.refresh(feed)

    return FeedResponse(Feed=feed.__dict__)


@alog
async def _cache_feeds(db: Session, cache_feeds_scope: str) -> FeedCacheResponse:
    # logic to save 'feeds_to_cache' in cache (worker)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint not yet supported.")


@alog
async def _fetch_from_feed(db: Session, feed_id: int) -> FeedFetchResponse:
    # logic to start the pull process (worker)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint not yet supported.")


@alog
async def _get_feed_details(db: Session, feed_id: int) -> FeedResponse:
    feed: Feed | None = await db.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    return FeedResponse(Feed=feed.__dict__)


@alog
async def _update_feed(db: Session, feed_id: int, body: FeedUpdateBody) -> FeedResponse:
    feed: Feed | None = await db.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    feed.patch(**body.model_dump(exclude_unset=True))

    await db.flush()
    await db.refresh(feed)

    return FeedResponse(Feed=feed.__dict__)


@alog
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

    await db.flush()

    return FeedEnableDisableResponse(name=feed.name, message=message, url=feed.url)


@alog
async def _fetch_data_from_all_feeds(db: Session) -> FeedFetchResponse:
    # logic to start the pull process for all feeds
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Endpoint not yet supported.")


@alog
async def _get_feeds(db: Session) -> list[FeedResponse]:
    result = await db.execute(select(Feed))
    feeds: Sequence[Feed] = result.scalars().all()

    return [FeedResponse(Feed=feed.__dict__) for feed in feeds]


@alog
async def _enable_feed(db: Session, feed_id: int) -> FeedEnableDisableResponse:
    feed: Feed | None = await db.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    if feed.enabled:
        message = "Feed already enabled."
    else:
        feed.enabled = True
        await db.flush()
        message = "Feed enabled successfully."

    return FeedEnableDisableResponse(name=feed.name, message=message, url=feed.url)


@alog
async def _disable_feed(db: Session, feed_id: int) -> FeedEnableDisableResponse:
    feed: Feed | None = await db.get(Feed, feed_id)

    if not feed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Feed not found.")

    if not feed.enabled:
        message = "Feed already disabled."
    else:
        feed.enabled = False
        await db.flush()
        message = "Feed disabled successfully."

    return FeedEnableDisableResponse(name=feed.name, message=message, url=feed.url)
