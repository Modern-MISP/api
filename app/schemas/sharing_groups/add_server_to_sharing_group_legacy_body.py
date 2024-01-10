from pydantic import BaseModel


class AddServerToSharingGroupLegacyBody(BaseModel):
    all_orgs: bool | None = None
