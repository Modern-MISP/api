from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db

# from ..models.feed import Feed
from ..schemas.feeds.get_all_feeds_response import FeedsResponse
from ..schemas.feeds.get_feed_response import FeedResponse
from ..schemas.feeds.create_update_feed_body import FeedAddUpdateBody
from ..schemas.feeds.enable_disable_feed_response import FeedEnableDisableResponse
from ..schemas.feeds.toggle_feed_body import FeedToggleBody
from ..schemas.feeds.cache_feed_response import FeedCacheResponse
from ..schemas.feeds.fetch_feeds_response import FeedFetchResponse


router = APIRouter(prefix="/feeds", tags=["feeds"])


@router.get("/")
async def get_feeds(db: Session = Depends(get_db)) -> List[FeedsResponse]:
    return []

    # try:
    #     feeds = db.query(Feed).all()
    #     return feeds
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


@router.get("/view/{feedId}")
@router.get("/{feed_id}")
async def get_feed_details(feed_id: str, db: Session = Depends(get_db)) -> FeedResponse:
    return FeedResponse(feed=[])

    # feed = db.query(Feed).filter(Feed.id == feed_id).first()
    # if feed is None:
    #     raise HTTPException(status_code=404, detail="Feed not found")
    # return feed


@router.post("/add")
@router.post("/")
async def add_feed(
    body: FeedAddUpdateBody, db: Session = Depends(get_db)
) -> FeedResponse:
    return FeedResponse(feed=[])

    # new_feed = Feed(**feed_data.dict())
    # db.add(new_feed)
    # db.commit()
    # db.refresh(new_feed)
    # return new_feed


@router.put("/edit/{feedId}")
@router.put("/{feed_id}")
async def update_feed(
    feed_id: str, body: FeedAddUpdateBody, db: Session = Depends(get_db)
) -> FeedResponse:
    return FeedResponse(feed=[])

    # feed = db.query(Feed).filter(Feed.id == feed_id).first()
    # if feed is None:
    #     raise HTTPException(status_code=404, detail="Feed not found")
    # for key, value in feed_data.dict().items():
    #     setattr(feed, key, value)
    # db.commit()
    # db.refresh(feed)
    # return feed


@router.post("/enable/{feedId}")
async def enable_feed(
    feed_id: str, enable: bool, db: Session = Depends(get_db)
) -> FeedEnableDisableResponse:
    return FeedEnableDisableResponse(name="", message="", url="")


@router.post("/disable/{feedId}")
async def disable_feed(
    feed_id: str, disable: bool, db: Session = Depends(get_db)
) -> FeedEnableDisableResponse:
    return FeedEnableDisableResponse(name="", message="", url="")


@router.patch("/{feedId}")
async def toggle_feed(
    feed_id: str, body: FeedToggleBody, db: Session = Depends(get_db)
) -> FeedEnableDisableResponse:
    return FeedEnableDisableResponse(name="", message="", url="")

    # feed = db.query(Feed).filter(Feed.id == feed_id).first()
    # if feed is None:
    #     raise HTTPException(status_code=404, detail="Feed not found")
    # setattr(feed, "enabled", enable)
    # db.commit()
    # return {
    #     "message": f"Feed {'enabled' if enable else 'disabled'}",
    #     "feed_id": feed_id,
    # }


@router.post("/cacheFeeds/{cacheFeedsScope}")
async def cache_feeds(
    cache_feeds_scope: dict, db: Session = Depends(get_db)
) -> FeedCacheResponse:
    return FeedCacheResponse(name="", message="", url="", saved=False, success=False)


@router.post("/fetchFromFeed/{feedId}")
@router.get("/fetchFromFeed/{feedId}")
async def fetch_from_feed(
    feed_id: str, db: Session = Depends(get_db)
) -> FeedFetchResponse:
    return FeedFetchResponse(result="")


@router.post("/fetchFromAllFeeds")
@router.get("/fetchFromAllFeeds")
async def fetch_data_from_all_feeds(db: Session = Depends(get_db)) -> FeedFetchResponse:
    return FeedFetchResponse(result="")
