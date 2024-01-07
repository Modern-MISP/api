from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.feed import Feed
from ..schemas.feed_schema import FeedSchema


router = APIRouter(prefix="/feeds")


@router.get("/", response_model=List[FeedSchema])
async def get_feeds(db: Session = Depends(get_db)) -> List[Feed]:
    try:
        feeds = db.query(Feed).all()
        return feeds
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
