from pydantic import BaseModel


class DeleteSharingGroupLegacyOut(BaseModel):
    saved: bool
    success: bool
    id: str
    name: str
    message: str
    url: str
