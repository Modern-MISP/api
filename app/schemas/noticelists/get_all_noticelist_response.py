from pydantic import BaseModel

from .noticelist import Noticelist

class GetAllNoticelist(BaseModel):
    response: list[Noticelist]