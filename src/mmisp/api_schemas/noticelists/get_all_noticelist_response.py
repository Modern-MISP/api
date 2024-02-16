from pydantic import BaseModel

from .get_noticelist_response import NoticelistResponse


class GetAllNoticelistResponse(BaseModel):
    response: list[NoticelistResponse]

    class Config:
        orm_mode = True
