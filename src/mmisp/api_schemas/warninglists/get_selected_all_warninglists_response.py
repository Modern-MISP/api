from pydantic import BaseModel

from .warninglist import Warninglist


class GetSelectedAllWarninglistsResponse(BaseModel):
    response: list[Warninglist]

    class Config:
        orm_mode = True
