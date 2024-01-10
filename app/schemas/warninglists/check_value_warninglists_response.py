from pydantic import BaseModel

class NameWarninglist(BaseModel):
    id: str
    name: str

class CheckValueWarninglistsResponse(BaseModel):
    response: str
    NameWarninglist: list[NameWarninglist]