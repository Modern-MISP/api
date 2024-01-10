from pydantic import BaseModel

from .warninglists import Warninglist

class GetSelectedAllWarninglistsResponse(BaseModel):
    response: list[Warninglist]