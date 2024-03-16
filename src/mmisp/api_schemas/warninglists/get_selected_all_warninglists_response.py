from pydantic import BaseModel

from mmisp.api_schemas.warninglists.warninglist_response import WarninglistAttributes


class WarninglistsResponse(BaseModel):
    warninglist: WarninglistAttributes


class GetSelectedAllWarninglistsResponse(BaseModel):
    warninglists: list[WarninglistsResponse]

    class Config:
        orm_mode = True
