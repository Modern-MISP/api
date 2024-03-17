from pydantic import BaseModel

from mmisp.api_schemas.warninglists.warninglist_response import WarninglistAttributes


class WarninglistsResponse(BaseModel):
    Warninglist: WarninglistAttributes


class GetSelectedAllWarninglistsResponse(BaseModel):
    Warninglists: list[WarninglistsResponse]

    class Config:
        orm_mode = True
