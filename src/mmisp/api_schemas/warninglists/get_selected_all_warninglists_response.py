from pydantic import BaseModel

from .warninglist_response import WarninglistResponse


class GetSelectedAllWarninglistsResponse(BaseModel):
    response: list[WarninglistResponse]

    class Config:
        orm_mode = True
