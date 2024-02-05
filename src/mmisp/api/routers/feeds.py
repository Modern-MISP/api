from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
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


# sorted according to CRUD


@router.post(
    "/feeds/",
    summary="Add new feed",
    description="Add a new feed with given details.",
    response_model=partial(FeedResponse),
)
async def add_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    body: FeedCreateAndUpdateBody,
    db: Session = Depends(get_db),
) -> dict:
    return await _add_feed_internal(body, db)


@router.post(  # TODO @worker
    "/feeds/cache_feeds/{cacheFeedsScope}",
    summary="Cache feeds",
    description="Cache feeds based on a specific scope.",
    response_model=partial(FeedCacheResponse),
)
async def cache_feeds(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Session = Depends(get_db),
    cache_feeds_scope: str = Path(..., alias="cacheFeedsScope"),
) -> dict:
    return await _cache_feeds_internal(db, cache_feeds_scope)


@router.get(  # TODO @worker
    "/feeds/fetch_from_feed/{feedId}",
    summary="Fetch from feed",
    description="Fetch data from a specific feed by its ID.",
    response_model=partial(FeedFetchResponse),
)
async def fetch_from_feed(
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _fetch_from_feed_internal(db, feed_id)


@router.get(
    "/feeds/{feedId}",
    summary="Get feed details",
    description="Retrieve details of a specific feed by its ID.",
    # response_model=partial(FeedResponse),  # todo: partial method does not work yet for this case
)
async def get_feed_details(
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _get_feed_details_internal(db, feed_id)


@router.put(
    "/feeds/{feedId}",
    summary="Update feed",
    description="Update an existing feed by its ID.",
    # response_model=partial(FeedResponse),  # todo: partial method does not work yet for this case
)
async def update_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    body: FeedCreateAndUpdateBody,
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _update_feed_internal(body, db, feed_id)


@router.patch(
    "/feeds/{feedId}",
    summary="Toggle feed status",
    description="Toggle the status of a feed between enabled and disabled.",
    response_model=partial(FeedEnableDisableResponse),
)
async def toggle_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    body: FeedToggleBody,
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _toggle_feed_internal(body, db, feed_id)


@router.get(  # TODO @ worker
    "/feeds/fetch_from_all_feeds",
    summary="Fetch from all feeds",
    description="Fetch data from all available feeds.",
    # response_model=partial(FeedFetchResponse),  # todo: partial method does not work yet for this case
)
async def fetch_data_from_all_feeds(db: Session = Depends(get_db)) -> dict:
    return await _fetch_data_from_all_feeds_internal(db)


@router.get(
    "/feeds/",
    summary="Get all feeds",
    description="Retrieve a list of all feeds.",
    # response_model=list[partial(FeedResponse)],  # type: ignore
)
async def get_feeds(db: Session = Depends(get_db)) -> list[FeedResponse]:
    return await _get_feeds_internal(db)


# # --- depricated ---


@router.post(
    "/feeds/add",
    deprecated=True,
    summary="Add new feed (Deprecated)",
    description="Deprecated. Add a new feed with given details using the old route.",
    # response_model=partial(FeedResponse),  # todo: partial method does not work yet for this case
)
async def add_feed_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    body: FeedCreateAndUpdateBody,
    db: Session = Depends(get_db),
) -> dict:
    return await _add_feed_internal(body, db)


@router.post(
    "/feeds/enable/{feedId}",
    deprecated=True,
    summary="Enable feed (Deprecated)",
    description="Deprecated. Enable a specific feed by its ID using the old route.",
    # response_model=partial(FeedEnableDisableResponse),  # todo: partial method does not work yet for this case
)
async def enable_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _enable_feed_internal(db, feed_id)


@router.post(
    "/feeds/disable/{feedId}",
    deprecated=True,
    summary="Disable feed (Deprecated)",
    description="Deprecated. Disable a specific feed by its ID using the old route.",
    # response_model=partial(FeedEnableDisableResponse),  # todo: partial method does not work yet for this case
)
async def disable_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _disable_feed_internal(db, feed_id)


@router.post(  # TODO @worker
    "/feeds/cacheFeeds/{cacheFeedsScope}",
    deprecated=True,
    summary="Cache feeds",
    description="Cache feeds based on a specific scope.",
    # response_model=partial(FeedCacheResponse),  # todo: partial method does not work yet for this case
)
async def cache_feeds_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Session = Depends(get_db),
    cache_feeds_scope: str = Path(..., alias="cacheFeedsScope"),
) -> dict:
    return await _cache_feeds_internal(db, cache_feeds_scope)


@router.post(  # TODO @worker
    "/feeds/fetchFromFeed/{feedId}",
    deprecated=True,
    summary="Fetch from feed (Deprecated)",
    description="Deprecated. Fetch data from a specific feed by its ID using the old route.",
    # response_model=partial(FeedFetchResponse),  # todo: partial method does not work yet for this case
)
async def fetch_from_feed_depr(
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _fetch_from_feed_internal(db, feed_id)


@router.post(  # TODO
    "/feeds/fetchFromAllFeeds",
    deprecated=True,
    summary="Fetch from all feeds (Deprecated)",
    description="Deprecated. Fetch data from all available feeds using the old route.",
    # response_model=partial(FeedFetchResponse),  # todo: partial method does not work yet for this case
)
async def fetch_data_from_all_feeds_depr(db: Session = Depends(get_db)) -> dict:
    return await _fetch_data_from_all_feeds_internal(db)


@router.get(
    "/feeds/view/{feedId}",
    deprecated=True,
    summary="Get feed details (Deprecated)",
    description="Deprecated. Retrieve details of a specific feed by its ID using the old route.",
    # response_model=partial(FeedResponse),  # todo: partial method does not work yet for this case
)
async def get_feed_details_depr(
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _get_feed_details_internal(db, feed_id)


@router.put(
    "/feeds/edit/{feedId}",
    deprecated=True,
    summary="Update feed (Deprecated)",
    description="Deprecated. Update an existing feed by its ID using the old route.",
    # response_model=partial(FeedResponse),  # todo: partial method does not work yet for this case
)
async def update_feed_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    body: FeedCreateAndUpdateBody,
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _update_feed_internal(body, db, feed_id)


# --- endpoint logic ---


async def _add_feed_internal(
    body: FeedCreateAndUpdateBody,
    db: Session,
) -> dict:
    new_feed = Feed(
        name=body.name,
        provider=body.provider,
        url=body.url,
        rules=body.rules,
        enabled=body.enabled,
        distribution=body.distribution,
        sharing_group_id=body.sharing_group_id,
        tag_id=body.tag_id,
        source_format=body.source_format,
        fixed_event=body.fixed_event,
        delta_merge=body.delta_merge,
        event_id=body.event_id,
        publish=body.publish,
        override_ids=body.override_ids,
        input_source=body.input_source,
        delete_local_file=body.delete_local_file,
        lookup_visible=body.lookup_visible,
        headers=body.headers,
        caching_enabled=body.caching_enabled,
        force_to_ids=body.force_to_ids,
        orgc_id=body.orgc_id,
    )

    db.add(new_feed)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    db.refresh(new_feed)

    feed_data = FeedAttributesResponse(
        id=str(new_feed.id),
        name=new_feed.name,
        provider=new_feed.provider,
        url=new_feed.url,
        rules=new_feed.rules,
        enabled=new_feed.enabled,
        distribution=new_feed.distribution,
        sharing_group_id=str(new_feed.sharing_group_id) if new_feed.sharing_group_id is not None else None,
        tag_id=str(new_feed.tag_id) if new_feed.tag_id is not None else None,
        default=new_feed.default,
        source_format=new_feed.source_format,
        fixed_event=new_feed.fixed_event,
        delta_merge=new_feed.delta_merge,
        event_id=str(new_feed.event_id) if new_feed.event_id is not None else None,
        publish=new_feed.publish,
        override_ids=new_feed.override_ids,
        settings=new_feed.settings,
        input_source=new_feed.input_source,
        delete_local_file=new_feed.delete_local_file,
        lookup_visible=new_feed.lookup_visible,
        headers=new_feed.headers,
        caching_enabled=new_feed.caching_enabled,
        force_to_ids=new_feed.force_to_ids,
        orgc_id=str(new_feed.orgc_id) if new_feed.orgc_id is not None else None,
        cache_timestamp=new_feed.cache_timestamp,
        cached_elements=str(new_feed.cached_elements) if new_feed.cached_elements is not None else None,
        coverage_by_other_feeds=new_feed.coverage_by_other_feeds,
    )

    return FeedResponse(feed=[feed_data])


async def _cache_feeds_internal(
    db: Session,
    cache_feeds_scope: str,
) -> dict:
    try:
        feeds_to_cache = db.query(Feed).filter(Feed.scope == cache_feeds_scope).all()  # noqa: F841

        # todo: logic to save 'feeds_to_cache' in cache (worker)

        success = True
        message = "Feeds successfully cached" if success else "Caching failed"

        return FeedCacheResponse(  # todo: make dynamic, according to the response from workers
            name="Caching Operation",
            message=message,
            url="",
            saved=True,
            success=success,
        )
    except Exception as e:  # if cach scope is invalid
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


async def _fetch_from_feed_internal(
    db: Session,
    feed_id: str,
) -> dict:
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    # todo: logic to start the pull process (worker)

    return FeedFetchResponse(result="Pull queued for background execution.")


async def _get_feed_details_internal(
    db: Session,
    feed_id: str,
) -> dict:
    feed = db.query(Feed).filter(Feed.id == feed_id).first()

    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    feed_data = FeedAttributesResponse(
        id=str(feed.id),
        name=feed.name,
        provider=feed.provider,
        url=feed.url,
        rules=feed.rules,
        enabled=feed.enabled,
        distribution=feed.distribution,
        sharing_group_id=str(feed.sharing_group_id),
        tag_id=str(feed.tag_id),
        default=feed.default,
        source_format=feed.source_format,
        fixed_event=feed.fixed_event,
        delta_merge=feed.delta_merge,
        event_id=str(feed.event_id),
        publish=feed.publish,
        override_ids=feed.override_ids,
        settings=feed.settings,
        input_source=feed.input_source,
        delete_local_file=feed.delete_local_file,
        lookup_visible=feed.lookup_visible,
        headers=feed.headers,
        caching_enabled=feed.caching_enabled,
        force_to_ids=feed.force_to_ids,
        orgc_id=str(feed.orgc_id),
        cache_timestamp=feed.cache_timestamp,
        cached_elements=str(feed.cached_elements),
        coverage_by_other_feeds=feed.coverage_by_other_feeds,
    )

    return FeedResponse(feed=[feed_data])


async def _update_feed_internal(
    body: FeedCreateAndUpdateBody,
    db: Session,
    feed_id: str,
) -> dict:
    feed = db.query(Feed).filter(Feed.id == feed_id).first()

    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    feed.name = body.name
    feed.provider = body.provider
    feed.url = body.url
    feed.rules = body.rules
    feed.enabled = body.enabled
    feed.distribution = body.distribution
    feed.sharing_group_id = body.sharing_group_id
    feed.tag_id = body.tag_id
    feed.source_format = body.source_format
    feed.fixed_event = body.fixed_event
    feed.delta_merge = body.delta_merge
    feed.event_id = body.event_id
    feed.publish = body.publish
    feed.override_ids = body.override_ids
    feed.input_source = body.input_source
    feed.delete_local_file = body.delete_local_file
    feed.lookup_visible = body.lookup_visible
    feed.headers = body.headers
    feed.caching_enabled = body.caching_enabled
    feed.force_to_ids = body.force_to_ids
    feed.orgc_id = body.orgc_id

    db.add(feed)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    db.refresh(feed)

    feed_data = FeedAttributesResponse(
        id=str(feed.id),
        name=str(feed.name),
        provider=str(feed.provider),
        url=str(feed.url),
        rules=str(feed.rules),
        enabled=bool(feed.enabled),
        distribution=bool(feed.distribution),
        sharing_group_id=str(feed.sharing_group_id),
        tag_id=str(feed.tag_id),
        default=bool(feed.default),
        source_format=str(feed.source_format),
        fixed_event=bool(feed.fixed_event),
        delta_merge=bool(feed.delta_merge),
        event_id=str(feed.event_id),
        publish=bool(feed.publish),
        override_ids=bool(feed.override_ids),
        settings=str(feed.settings),
        input_source=str(feed.input_source),
        delete_local_file=bool(feed.delete_local_file),
        lookup_visible=bool(feed.lookup_visible),
        headers=str(feed.headers),
        caching_enabled=bool(feed.caching_enabled),
        force_to_ids=bool(feed.force_to_ids),
        orgc_id=str(feed.orgc_id),
        cache_timestamp=str(feed.cache_timestamp),
        cached_elements=str(feed.cached_elements),
        coverage_by_other_feeds=str(feed.coverage_by_other_feeds),
    )

    return FeedResponse(feed=[feed_data])


async def _toggle_feed_internal(
    body: FeedToggleBody,
    db: Session,
    feed_id: str,
) -> dict:
    feed = db.query(Feed).filter(Feed.id == feed_id).first()

    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    message = ""

    if body.enable and not feed.enabled:
        feed.enabled = True
        message = "Feed enabled successfully"
    elif not body.enable and feed.enabled:
        feed.enabled = False
        message = "Feed disabled successfully"
    elif body.enable and feed.enabled:
        message = "Feed already enabled"
    elif not body.enable and not feed.enabled:
        message = "Feed already disabled"

    db.commit()

    return FeedEnableDisableResponse(name=feed.name, message=message, url=feed.url)


async def _fetch_data_from_all_feeds_internal(db: Session) -> dict:
    feeds = db.query(Feed).all()  # noqa: F841

    # todo: logic to start the pull process

    fetched_data = ""

    return FeedFetchResponse(result=fetched_data)


async def _get_feeds_internal(db: Session) -> list[dict]:
    feeds = db.query(Feed).all()

    feed_responses = [
        FeedAttributesResponse(
            id=str(feed.id),
            name=feed.name,
            provider=feed.provider,
            url=feed.url,
            rules=feed.rules,
            enabled=feed.enabled,
            distribution=feed.distribution,
            sharing_group_id=str(feed.sharing_group_id),
            tag_id=str(feed.tag_id),
            default=feed.default,
            source_format=feed.source_format,
            fixed_event=feed.fixed_event,
            delta_merge=feed.delta_merge,
            event_id=str(feed.event_id),
            publish=feed.publish,
            override_ids=feed.override_ids,
            settings=feed.settings,
            input_source=feed.input_source,
            delete_local_file=feed.delete_local_file,
            lookup_visible=feed.lookup_visible,
            headers=feed.headers,
            caching_enabled=feed.caching_enabled,
            force_to_ids=feed.force_to_ids,
            orgc_id=str(feed.orgc_id),
            cache_timestamp=feed.cache_timestamp,
            cached_elements=str(feed.cached_elements),
            coverage_by_other_feeds=feed.coverage_by_other_feeds,
        )
        for feed in feeds
    ]

    return [FeedResponse(feed=feed_responses)]


async def _enable_feed_internal(
    db: Session,
    feed_id: str,
) -> dict:
    try:
        int(feed_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid feed ID")

    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    feed.enabled = True  # type: ignore
    db.commit()

    return FeedEnableDisableResponse(name=str(feed.name), message="Feed successfully enabled", url=str(feed.url))


async def _disable_feed_internal(
    db: Session,
    feed_id: str,
) -> dict:
    try:
        int(feed_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid feed ID")

    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    feed.enabled = False  # type: ignore
    db.commit()

    return FeedEnableDisableResponse(name=str(feed.name), message="Feed successfully disabled", url=str(feed.url))
