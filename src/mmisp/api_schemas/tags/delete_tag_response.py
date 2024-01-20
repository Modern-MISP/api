from pydantic import BaseModel


class TagDeleteResponse(BaseModel):
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True
