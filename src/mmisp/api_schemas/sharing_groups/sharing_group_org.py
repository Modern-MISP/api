from pydantic import BaseModel


class SharingGroupOrg(BaseModel):
    id: str
    sharing_group_id: str
    org_id: str
    extend: bool
