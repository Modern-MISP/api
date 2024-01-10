from pydantic import BaseModel

from .warninglists import Warninglist

class GetSelectedWarninglistsBody(BaseModel):
    response: list[Warninglist]