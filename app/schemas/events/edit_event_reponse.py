from pydantic import BaseModel


class EventEditResponse(BaseModel):
    class Config:
        orm_mode: True
