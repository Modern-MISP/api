from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.feed import Feed
from ..schemas.feed_schema import (
    FeedSchema,
    FeedViewSchema,
    FeedTogleSchema,
    FeedCacheSchema,
    FeedFetchSchema,
)

router = APIRouter(prefix="/feeds")


@router.get("/", response_model=List[FeedSchema])
async def get_feeds(db: Session = Depends(get_db)) -> List[Feed]:
    try:
        feeds = db.query(Feed).all()
        return feeds
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/view/{feedId}", response_model=FeedViewSchema)
@router.get("/{feed_id}", response_model=FeedViewSchema)
async def get_feed_details(feed_id: str, db: Session = Depends(get_db)) -> Feed:
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    return feed


@router.post("/add", response_model=FeedSchema)
async def add_feed(feed_data: FeedSchema, db: Session = Depends(get_db)) -> Feed:
    new_feed = Feed(**feed_data.dict())
    db.add(new_feed)
    db.commit()
    db.refresh(new_feed)
    return new_feed


@router.put("/edit/{feedId}", response_model=FeedSchema)
@router.put("/{feed_id}", response_model=FeedSchema)
async def update_feed(
    feed_id: str, feed_data: FeedSchema, db: Session = Depends(get_db)
) -> Feed:
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    for key, value in feed_data.dict().items():
        setattr(feed, key, value)
    db.commit()
    db.refresh(feed)
    return feed


@router.post("/enable/{feedId}", response_model=FeedTogleSchema)
async def enable_feed(
    feed_id: str, enable: bool, db: Session = Depends(get_db)
) -> None:
    pass


@router.post("/disable/{feedId}", response_model=FeedTogleSchema)
async def disable_feed(
    feed_id: str, disable: bool, db: Session = Depends(get_db)
) -> None:
    pass


@router.patch("/{feedId}", response_model=FeedTogleSchema)
async def toggle_feed(
    feed_id: str, enable: bool, db: Session = Depends(get_db)
) -> dict:
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    setattr(feed, "enabled", enable)
    db.commit()
    return {
        "message": f"Feed {'enabled' if enable else 'disabled'}",
        "feed_id": feed_id,
    }


@router.post("/cacheFeeds/{cacheFeedsScope}", response_model=FeedCacheSchema)
async def cache_feeds(cache_feeds_scope: dict, db: Session = Depends(get_db)) -> None:
    pass


@router.post("/fetchFromFeed/{feedId}", response_model=FeedFetchSchema)
@router.get("/fetchFromFeed/{feedId}", response_model=FeedFetchSchema)
async def fetch_from_feed(feed_id: str, db: Session = Depends(get_db)) -> None:
    pass


@router.post("/fetchFromAllFeeds", response_model=FeedFetchSchema)
@router.get("/fetchFromAllFeeds", response_model=FeedFetchSchema)
async def fetch_data_from_all_feeds(db: Session = Depends(get_db)) -> None:
    pass
