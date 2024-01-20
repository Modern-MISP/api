from pydantic import BaseModel


class AddOrgToSharingGroupLegacyBody(BaseModel):
    extend: bool | None = None
