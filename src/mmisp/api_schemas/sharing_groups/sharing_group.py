from datetime import datetime

from pydantic import BaseModel


class SharingGroup(BaseModel):
    id: str
    name: str
    releasability: str
    description: str
    uuid: str
    organisation_uuid: str
    org_id: str
    sync_user_id: str
    active: bool
    created: datetime
    modified: datetime
    local: bool
    roaming: bool
