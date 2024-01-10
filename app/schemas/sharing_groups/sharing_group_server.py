from pydantic import BaseModel


class SharingGroupServer(BaseModel):
    id: str
    sharing_group_id: str
    server_id: str
    all_orgs: bool
