from pydantic import BaseModel

from mmisp.api_schemas.warninglists.warninglist_response import WarninglistAttributes


class GetSelectedAllWarninglistsResponse(BaseModel):
    response: list[WarninglistAttributes]

    class Config:
        orm_mode = True
