from pydantic import BaseModel


class AddOrgToSharingGroupBody(BaseModel):
    organizationId: str
    extend: bool | None = None
