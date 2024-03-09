from pydantic import BaseModel

from mmisp.api_schemas.noticelists.get_noticelist_response import NoticelistAttributesResponse


class GetAllNoticelistResponse(BaseModel):
    response: list[NoticelistAttributesResponse]

    class Config:
        orm_mode = True
