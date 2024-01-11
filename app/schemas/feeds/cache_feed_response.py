from pydantic import BaseModel


class FeedCacheResponse(BaseModel):
    name: str
    message: str
    url: str
    saved: bool  # new
    success: bool  # new

    class Config:
        orm_mode = True
