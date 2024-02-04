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

router = APIRouter(tags=["feeds"])


# Sorted according to CRUD


@router.post(
    "/feeds/add",
    deprecated=True,
    summary="Add new feed (Deprecated)",
    description="Deprecated. Add a new feed with given details using the old route.",
)
@router.post("/feeds/", summary="Add new feed", description="Add a new feed with given details.")
async def add_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    body: FeedCreateAndUpdateBody,
    db: Session = Depends(get_db),
) -> FeedResponse:
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


@router.post(
    "/feeds/enable/{feedId}",
    deprecated=True,
    summary="Enable feed (Deprecated)",
    description="Deprecated. Enable a specific feed by its ID using the old route.",
)
async def enable_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> FeedEnableDisableResponse:
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


@router.post(
    "/feeds/disable/{feedId}",
    deprecated=True,
    summary="Disable feed (Deprecated)",
    description="Deprecated. Disable a specific feed by its ID using the old route.",
)
async def disable_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> FeedEnableDisableResponse:
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


@router.post(  # TODO @worker
    "/feeds/cacheFeeds/{cacheFeedsScope}", summary="Cache feeds", description="Cache feeds based on a specific scope."
)
async def cache_feeds(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Session = Depends(get_db),
    cache_feeds_scope: str = Path(..., alias="cacheFeedsScope"),
) -> FeedCacheResponse:
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


@router.post(  # TODO @worker
    "/feeds/fetchFromFeed/{feedId}",
    deprecated=True,
    summary="Fetch from feed (Deprecated)",
    description="Deprecated. Fetch data from a specific feed by its ID using the old route.",
)
@router.get(
    "/feeds/fetchFromFeed/{feedId}", summary="Fetch from feed", description="Fetch data from a specific feed by its ID."
)
async def fetch_from_feed(
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> FeedFetchResponse:
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    # todo: logic to start the pull process (worker)

    return FeedFetchResponse(result="Pull queued for background execution.")


@router.get(
    "/feeds/view/{feedId}",
    deprecated=True,
    summary="Get feed details (Deprecated)",
    description="Deprecated. Retrieve details of a specific feed by its ID using the old route.",
)
@router.get("/feeds/{feedId}", summary="Get feed details", description="Retrieve details of a specific feed by its ID.")
async def get_feed_details(
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> FeedResponse:
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


@router.put(
    "/feeds/edit/{feedId}",
    deprecated=True,
    summary="Update feed (Deprecated)",
    description="Deprecated. Update an existing feed by its ID using the old route.",
)
@router.put("/feeds/{feedId}", summary="Update feed", description="Update an existing feed by its ID.")
async def update_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    body: FeedCreateAndUpdateBody,
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> FeedResponse:
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


@router.patch(
    "/feeds/{feedId}",
    summary="Toggle feed status",
    description="Toggle the status of a feed between enabled and disabled.",
)
async def toggle_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    body: FeedToggleBody,
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> FeedEnableDisableResponse:
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


@router.post(  # TODO
    "/feeds/fetchFromAllFeeds",
    deprecated=True,
    summary="Fetch from all feeds (Deprecated)",
    description="Deprecated. Fetch data from all available feeds using the old route.",
)
@router.get(
    "/feeds/fetchFromAllFeeds", summary="Fetch from all feeds", description="Fetch data from all available feeds."
)
async def fetch_data_from_all_feeds(db: Session = Depends(get_db)) -> FeedFetchResponse:
    feeds = db.query(Feed).all()  # noqa: F841

    # todo: logic to start the pull process

    fetched_data = ""

    return FeedFetchResponse(result=fetched_data)


@router.get("/feeds/", summary="Get all feeds", description="Retrieve a list of all feeds.")
async def get_feeds(db: Session = Depends(get_db)) -> list[FeedResponse]:
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
