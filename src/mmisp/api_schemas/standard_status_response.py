from pydantic import BaseModel


class StandardStatusResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str


class StandardStatusIdentifiedResponse(StandardStatusResponse):
    id: str
