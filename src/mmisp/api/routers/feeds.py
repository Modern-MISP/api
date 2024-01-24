from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# from ..models.feed import Feed
from mmisp.api_schemas.feeds.cache_feed_response import FeedCacheResponse
from mmisp.api_schemas.feeds.create_update_feed_body import FeedCreateAndUpdateBody
from mmisp.api_schemas.feeds.enable_disable_feed_response import FeedEnableDisableResponse
from mmisp.api_schemas.feeds.fetch_feeds_response import FeedFetchResponse
from mmisp.api_schemas.feeds.get_feed_response import FeedResponse
from mmisp.api_schemas.feeds.toggle_feed_body import FeedToggleBody
from mmisp.db.database import get_db

router = APIRouter(prefix="/feeds", tags=["feeds"])


@router.get("/", summary="Get all feeds", description="Retrieve a list of all feeds.")
async def get_feeds(db: Session = Depends(get_db)) -> list[FeedResponse]:
    # Logic to fetch feeds goes here

    # try:
    #     feeds = db.query(Feed).all()
    #     return feeds
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

    return []


@router.get(
    "/view/{feedId}",
    deprecated=True,
    summary="Get feed details (Deprecated)",
    description="Deprecated. Retrieve details of a specific feed by its ID using the old route.",
)
@router.get("/{feedId}", summary="Get feed details", description="Retrieve details of a specific feed by its ID.")
async def get_feed_details(feed_id: str, db: Session = Depends(get_db)) -> FeedResponse:
    # Logic to get feed details goes here

    # feed = db.query(Feed).filter(Feed.id == feed_id).first()
    # if feed is None:
    #     raise HTTPException(status_code=404, detail="Feed not found")
    # return feed

    return FeedResponse(feed=[])


@router.post(
    "/add",
    deprecated=True,
    summary="Add new feed (Deprecated)",
    description="Deprecated. Add a new feed with given details using the old route.",
)
@router.post("/", summary="Add new feed", description="Add a new feed with given details.")
async def add_feed(body: FeedCreateAndUpdateBody, db: Session = Depends(get_db)) -> FeedResponse:
    # Logic to add a new feed goes here

    # new_feed = Feed(**feed_data.dict())
    # db.add(new_feed)
    # db.commit()
    # db.refresh(new_feed)
    # return new_feed

    return FeedResponse(feed=[])


@router.put(
    "/edit/{feedId}",
    deprecated=True,
    summary="Update feed (Deprecated)",
    description="Deprecated. Update an existing feed by its ID using the old route.",
)
@router.put("/{feedId}", summary="Update feed", description="Update an existing feed by its ID.")
async def update_feed(feed_id: str, body: FeedCreateAndUpdateBody, db: Session = Depends(get_db)) -> FeedResponse:
    # Logic to update feed goes here

    # feed = db.query(Feed).filter(Feed.id == feed_id).first()
    # if feed is None:
    #     raise HTTPException(status_code=404, detail="Feed not found")
    # for key, value in feed_data.dict().items():
    #     setattr(feed, key, value)
    # db.commit()
    # db.refresh(feed)
    # return feed

    return FeedResponse(feed=[])


@router.post(
    "/enable/{feedId}",
    deprecated=True,
    summary="Enable feed (Deprecated)",
    description="Deprecated. Enable a specific feed by its ID using the old route.",
)
async def enable_feed(feed_id: str, db: Session = Depends(get_db)) -> FeedEnableDisableResponse:
    # Logic to enable a feed goes here

    return FeedEnableDisableResponse(name="", message="", url="")


@router.post(
    "/disable/{feedId}",
    deprecated=True,
    summary="Disable feed (Deprecated)",
    description="Deprecated. Disable a specific feed by its ID using the old route.",
)
async def disable_feed(feed_id: str, db: Session = Depends(get_db)) -> FeedEnableDisableResponse:
    # Logic to disable a feed goes here

    return FeedEnableDisableResponse(name="", message="", url="")


@router.patch(
    "/{feedId}", summary="Toggle feed status", description="Toggle the status of a feed between enabled and disabled."
)
async def toggle_feed(feed_id: str, body: FeedToggleBody, db: Session = Depends(get_db)) -> FeedEnableDisableResponse:
    # Logic to toggle feed status goes here

    # feed = db.query(Feed).filter(Feed.id == feed_id).first()
    # if feed is None:
    #     raise HTTPException(status_code=404, detail="Feed not found")
    # setattr(feed, "enabled", enable)
    # db.commit()
    # return {
    #     "message": f"Feed {'enabled' if enable else 'disabled'}",
    #     "feed_id": feed_id,
    # }

    return FeedEnableDisableResponse(name="", message="", url="")


@router.post(
    "/cacheFeeds/{cacheFeedsScope}", summary="Cache feeds", description="Cache feeds based on a specific scope."
)
async def cache_feeds(cache_feeds_scope: dict, db: Session = Depends(get_db)) -> FeedCacheResponse:
    # Logic to cache feeds goes here

    return FeedCacheResponse(name="", message="", url="", saved=False, success=False)


@router.post(
    "/fetchFromFeed/{feedId}",
    deprecated=True,
    summary="Fetch from feed (Deprecated)",
    description="Deprecated. Fetch data from a specific feed by its ID using the old route.",
)
@router.get(
    "/fetchFromFeed/{feedId}", summary="Fetch from feed", description="Fetch data from a specific feed by its ID."
)
async def fetch_from_feed(feed_id: str, db: Session = Depends(get_db)) -> FeedFetchResponse:
    # Logic to fetch from feed goes here

    return FeedFetchResponse(result="")


@router.post(
    "/fetchFromAllFeeds",
    deprecated=True,
    summary="Fetch from all feeds (Deprecated)",
    description="Deprecated. Fetch data from all available feeds using the old route.",
)
@router.get("/fetchFromAllFeeds", summary="Fetch from all feeds", description="Fetch data from all available feeds.")
async def fetch_data_from_all_feeds(db: Session = Depends(get_db)) -> FeedFetchResponse:
    # Logic to fetch from all feeds goes here

    return FeedFetchResponse(result="")
