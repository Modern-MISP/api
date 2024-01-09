from pydantic import BaseModel


class FeedEnableDisableResponse(BaseModel):
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True
