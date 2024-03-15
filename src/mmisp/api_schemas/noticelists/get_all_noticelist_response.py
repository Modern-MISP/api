from pydantic import BaseModel

from mmisp.api_schemas.noticelists.get_noticelist_response import NoticelistAttributes


class GetAllNoticelist(BaseModel):
    Noticelist: NoticelistAttributes


class GetAllNoticelistResponse(BaseModel):
    response: list[GetAllNoticelist]

    class Config:
        orm_mode = True
