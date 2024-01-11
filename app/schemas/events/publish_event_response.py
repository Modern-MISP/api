from pydantic import BaseModel


class EventPublishResponse(BaseModel):
    name: str
    message: str
    url: str
    id: str

    class Config:
        orm_mode = True
