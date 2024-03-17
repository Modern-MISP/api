from pydantic import BaseModel

from mmisp.api_schemas.noticelists.get_noticelist_response import NoticelistAttributes


class GetAllNoticelists(BaseModel):
    Noticelist: NoticelistAttributes

    class Config:
        orm_mode = True
