from pydantic import BaseModel


class EditEventResponse(BaseModel):
    class Config:
        orm_mode = True
