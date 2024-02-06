import logging
from typing import Annotated

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

logging.basicConfig(
    level=logging.INFO  # todo: remove comment
)  # 'logger.error' for errors on the part of the user, 'logger.exception' for errors on the part of the server
logger = logging.getLogger(__name__)

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
    summary="Add new feed",
    description="Add a new feed with given details.",
    response_model=partial(FeedResponse),
    status_code=status.HTTP_201_CREATED,
)
async def add_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    body: FeedCreateAndUpdateBody,
    db: Session = Depends(get_db),
) -> dict:
    return await _add_feed(body, db)


@router.post(  #! @worker: also change 'description' and 'status_code'
    "/feeds/cache_feeds/{cacheFeedsScope}",
    summary="Cache feeds",
    description="Cache feeds based on a specific scope. NOT YET AVAILABLE!",
    response_model=partial(FeedCacheResponse),
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def cache_feeds(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Session = Depends(get_db),
    cache_feeds_scope: str = Path(..., alias="cacheFeedsScope"),
) -> dict:
    return await _cache_feeds(db, cache_feeds_scope)


@router.get(  #! @worker: also change 'description' and 'status_code'
    "/feeds/fetch_from_feed/{feedId}",
    summary="Fetch from feed",
    description="Fetch data from a specific feed by its ID. NOT YET AVAILABLE!",
    response_model=partial(FeedFetchResponse),
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def fetch_from_feed(
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _fetch_from_feed(db, feed_id)


@router.get(
    "/feeds/{feedId}",
    summary="Get feed details",
    description="Retrieve details of a specific feed by its ID.",
    # response_model=partial(FeedResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_200_OK,
)
async def get_feed_details(
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _get_feed_details(db, feed_id)


@router.put(
    "/feeds/{feedId}",
    summary="Update feed",
    description="Update an existing feed by its ID.",
    # response_model=partial(FeedResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_200_OK,
)
async def update_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    body: FeedCreateAndUpdateBody,
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _update_feed(body, db, feed_id)


@router.patch(
    "/feeds/{feedId}",
    summary="Toggle feed status",
    description="Toggle the status of a feed between enabled and disabled.",
    response_model=partial(FeedEnableDisableResponse),
    status_code=status.HTTP_200_OK,
)
async def toggle_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    body: FeedToggleBody,
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _toggle_feed(body, db, feed_id)


@router.get(  #! @worker: also change 'description' and 'status_code'
    "/feeds/fetch_from_all_feeds",
    summary="Fetch from all feeds",
    description="Fetch data from all available feeds. NOT YET AVAILABLE!",
    # response_model=partial(FeedFetchResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def fetch_data_from_all_feeds(db: Session = Depends(get_db)) -> dict:
    return await _fetch_data_from_all_feeds(db)


@router.get(
    "/feeds/",
    summary="Get all feeds",
    description="Retrieve a list of all feeds.",
    # response_model=list[partial(FeedResponse)],  # type: ignore # todo: partial method does not work yet for this case
    status_code=status.HTTP_200_OK,
)
async def get_feeds(db: Session = Depends(get_db)) -> list[FeedResponse]:
    return await _get_feeds(db)


# --- deprecated ---


@router.post(
    "/feeds/add",
    deprecated=True,
    summary="Add new feed (Deprecated)",
    description="Deprecated. Add a new feed with given details using the old route.",
    # response_model=partial(FeedResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_201_CREATED,
)
async def add_feed_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    body: FeedCreateAndUpdateBody,
    db: Session = Depends(get_db),
) -> dict:
    return await _add_feed(body, db)


@router.post(
    "/feeds/enable/{feedId}",
    deprecated=True,
    summary="Enable feed (Deprecated)",
    description="Deprecated. Enable a specific feed by its ID using the old route.",
    # response_model=partial(FeedEnableDisableResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_200_OK,
)
async def enable_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _enable_feed(db, feed_id)


@router.post(
    "/feeds/disable/{feedId}",
    deprecated=True,
    summary="Disable feed (Deprecated)",
    description="Deprecated. Disable a specific feed by its ID using the old route.",
    # response_model=partial(FeedEnableDisableResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_200_OK,
)
async def disable_feed(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _disable_feed(db, feed_id)


@router.post(  #! @worker
    "/feeds/cacheFeeds/{cacheFeedsScope}",
    deprecated=True,
    summary="Cache feeds",
    description="Cache feeds based on a specific scope.",
    # response_model=partial(FeedCacheResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def cache_feeds_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Session = Depends(get_db),
    cache_feeds_scope: str = Path(..., alias="cacheFeedsScope"),
) -> dict:
    return await _cache_feeds(db, cache_feeds_scope)


@router.post(  #! @worker
    "/feeds/fetchFromFeed/{feedId}",
    deprecated=True,
    summary="Fetch from feed (Deprecated)",
    description="Deprecated. Fetch data from a specific feed by its ID using the old route.",
    # response_model=partial(FeedFetchResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def fetch_from_feed_depr(
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _fetch_from_feed(db, feed_id)


@router.post(  #! @worker
    "/feeds/fetchFromAllFeeds",
    deprecated=True,
    summary="Fetch from all feeds (Deprecated)",
    description="Deprecated. Fetch data from all available feeds using the old route.",
    # response_model=partial(FeedFetchResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def fetch_data_from_all_feeds_depr(db: Session = Depends(get_db)) -> dict:
    return await _fetch_data_from_all_feeds(db)


@router.get(
    "/feeds/view/{feedId}",
    deprecated=True,
    summary="Get feed details (Deprecated)",
    description="Deprecated. Retrieve details of a specific feed by its ID using the old route.",
    # response_model=partial(FeedResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_200_OK,
)
async def get_feed_details_depr(
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _get_feed_details(db, feed_id)


@router.put(
    "/feeds/edit/{feedId}",
    deprecated=True,
    summary="Update feed (Deprecated)",
    description="Deprecated. Update an existing feed by its ID using the old route.",
    # response_model=partial(FeedResponse),  # todo: partial method does not work yet for this case
    status_code=status.HTTP_200_OK,
)
async def update_feed_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    body: FeedCreateAndUpdateBody,
    db: Session = Depends(get_db),
    feed_id: str = Path(..., alias="feedId"),
) -> dict:
    return await _update_feed(body, db, feed_id)


# --- endpoint logic ---


async def _add_feed(
    body: FeedCreateAndUpdateBody,
    db: Session,
) -> dict:
    if not body.name:
        logger.error("Feed creation failed: field 'name' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'name' is required.")
    if not body.provider:
        logger.error("Feed creation failed: field 'provider' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'provider' is required.")
    if not body.url:
        logger.error("Feed creation failed: field 'url' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'url' is required.")
    if not body.enabled:
        logger.error("Feed creation failed: field 'enabled' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'enabled' is required.")
    if not body.distribution:
        logger.error("Feed creation failed: field 'distribution' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'distribution' is required.")
    if not body.source_format:
        logger.error("Feed creation failed: field 'source_format' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'source_format' is required.")
    if not body.fixed_event:
        logger.error("Feed creation failed: field 'fixed_event' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'fixed_event' is required.")

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


async def _cache_feeds(
    db: Session,
    cache_feeds_scope: str,
) -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="ENDPOINT NOT YET SUPPORTED")

    # try:
    #     feeds_to_cache = db.query(Feed).filter(Feed.scope == cache_feeds_scope).all()  # noqa: F841

    #     #! logic to save 'feeds_to_cache' in cache (worker)

    #     # message = "Feeds successfully cached" if success else "Caching failed"
    #     message = "ENDPOINT NOT YET SUPPORTED"
    #     success = False
    #     saved = False

    #     return FeedCacheResponse(  # ? make dynamic, according to the response from workers
    #         name="Caching Operation",
    #         message=message,
    #         url="",
    #         saved=saved,
    #         success=success,
    #     )
    # except Exception as e:  # if cach scope is invalid
    #     logger.exception(f"Failed to cache feed: {e}")
    #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."


async def _fetch_from_feed(
    db: Session,
    feed_id: str,
) -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="ENDPOINT NOT YET SUPPORTED")

    # feed = db.get(Feed, feed_id)
    # if not feed:
    #     logger.error(f"Feed with id '{feed_id}' not found.")
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    #! logic to start the pull process (worker)

    # return FeedFetchResponse(result="Pull queued for background execution.")


async def _get_feed_details(
    db: Session,
    feed_id: str,
) -> dict:
    feed = db.get(Feed, feed_id)

    if not feed:
        logger.error(f"Feed with id '{feed_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

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


async def _update_feed(
    body: FeedCreateAndUpdateBody,
    db: Session,
    feed_id: str,
) -> dict:
    feed = db.get(Feed, feed_id)

    if not feed:
        logger.error(f"Feed with id '{feed_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    if not body.name:
        logger.error("Updating feed failed: field 'name' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'name' is required.")
    if not body.provider:
        logger.error("Updating feed failed: field 'provider' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'provider' is required.")
    if not body.url:
        logger.error("Updating feed failed: field 'url' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'url' is required.")
    if not body.enabled:
        logger.error("Updating feed failed: field 'enabled' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'enabled' is required.")
    if not body.distribution:
        logger.error("Updating feed failed: field 'distribution' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'distribution' is required.")
    if not body.source_format:
        logger.error("Updating feed failed: field 'source_format' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'source_format' is required.")
    if not body.fixed_event:
        logger.error("Updating feed failed: field 'fixed_event' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'fixed_event' is required.")

    updated_feed = Feed(
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

    feed_data = FeedAttributesResponse(
        id=str(updated_feed.id),
        name=str(updated_feed.name),
        provider=str(updated_feed.provider),
        url=str(updated_feed.url),
        rules=str(updated_feed.rules),
        enabled=bool(updated_feed.enabled),
        distribution=bool(updated_feed.distribution),
        sharing_group_id=str(updated_feed.sharing_group_id),
        tag_id=str(updated_feed.tag_id),
        default=bool(updated_feed.default),
        source_format=str(updated_feed.source_format),
        fixed_event=bool(updated_feed.fixed_event),
        delta_merge=bool(updated_feed.delta_merge),
        event_id=str(updated_feed.event_id),
        publish=bool(updated_feed.publish),
        override_ids=bool(updated_feed.override_ids),
        settings=str(updated_feed.settings),
        input_source=str(updated_feed.input_source),
        delete_local_file=bool(updated_feed.delete_local_file),
        lookup_visible=bool(updated_feed.lookup_visible),
        headers=str(updated_feed.headers),
        caching_enabled=bool(updated_feed.caching_enabled),
        force_to_ids=bool(updated_feed.force_to_ids),
        orgc_id=str(updated_feed.orgc_id),
        cache_timestamp=str(updated_feed.cache_timestamp),
        cached_elements=str(updated_feed.cached_elements),
        coverage_by_other_feeds=str(updated_feed.coverage_by_other_feeds),
    )

    return FeedResponse(feed=[feed_data])


async def _toggle_feed(
    body: FeedToggleBody,
    db: Session,
    feed_id: str,
) -> dict:
    feed = db.get(Feed, feed_id)

    if not feed:
        logger.error(f"Feed with id '{feed_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    if not body.enable:
        logger.error("Toggle feed failed: field 'enable' is required.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'enable' is required.")

    message = ""

    if body.enable == "True" and feed.enabled == "False":
        feed.enabled = "True"
        message = "Feed enabled successfully"
    elif body.enable == "False" and feed.enabled == "True":
        feed.enabled = "False"
        message = "Feed disabled successfully"
    elif body.enable == "True" and feed.enabled == "True":
        message = "Feed already enabled"
    elif body.enable == "False" and feed.enabled == "False":
        message = "Feed already disabled"

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
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="ENDPOINT NOT YET SUPPORTED")

    # feeds = db.query(Feed).all()  # noqa: F841

    # #! logic to start the pull process

    # fetched_data = ""

    # return FeedFetchResponse(result=fetched_data)


async def _get_feeds(db: Session) -> list[dict]:
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


async def _enable_feed(
    db: Session,
    feed_id: str,
) -> dict:
    try:
        int(feed_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid feed ID")

    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        logger.error(f"Feed with id '{feed_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    feed.enabled = True  # type: ignore

    try:
        db.commit()
        logger.info(f"Feed with id '{feed_id}' enabled.")
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to enable feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    return FeedEnableDisableResponse(name=str(feed.name), message="Feed successfully enabled", url=str(feed.url))


async def _disable_feed(
    db: Session,
    feed_id: str,
) -> dict:
    try:
        int(feed_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid feed ID")

    feed = db.get(Feed, feed_id)
    if not feed:
        logger.error(f"Feed with id '{feed_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")

    feed.enabled = False  # type: ignore

    try:
        db.commit()
        logger.info(f"Feed with id '{feed_id}' disabled.")
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to disable feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    return FeedEnableDisableResponse(name=str(feed.name), message="Feed successfully disabled", url=str(feed.url))
