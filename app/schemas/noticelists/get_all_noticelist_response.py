from pydantic import BaseModel

from .noticelist import Noticelist


class GetAllNoticelist(BaseModel):
    response: list[Noticelist]

    class Config:
        orm_mode = True
