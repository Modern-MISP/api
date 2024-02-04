from pydantic import BaseModel


class ObjectEventResponse(BaseModel):
    id: str
    info: str
    org_id: str | None = None
    orgc_id: str | None = None
