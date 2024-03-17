from pydantic import BaseModel


class FeedCacheResponse(BaseModel):
    name: str
    message: str
    url: str
    saved: bool
    success: bool

    class Config:
        orm_mode = True
