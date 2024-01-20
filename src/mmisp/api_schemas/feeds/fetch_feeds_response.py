from pydantic import BaseModel


class FeedFetchResponse(BaseModel):
    result: str

    class Config:
        orm_mode = True
