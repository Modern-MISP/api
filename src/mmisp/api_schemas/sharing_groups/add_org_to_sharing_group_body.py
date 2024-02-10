from pydantic import BaseModel


class AddOrgToSharingGroupBody(BaseModel):
    organisationId: str
    extend: bool | None = None
