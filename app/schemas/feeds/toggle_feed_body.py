from pydantic import BaseModel


class FeedToggleBody(BaseModel):
    enable: bool

    class Config:
        orm_mode = True
