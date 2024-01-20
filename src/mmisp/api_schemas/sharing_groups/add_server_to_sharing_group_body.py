from pydantic import BaseModel


class AddServerToSharingGroupBody(BaseModel):
    serverId: str
    all_orgs: bool | None = None
