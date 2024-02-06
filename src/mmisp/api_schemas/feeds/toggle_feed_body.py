from pydantic import BaseModel


class FeedToggleBody(BaseModel):
    enable: str

    class Config:
        orm_mode = True
