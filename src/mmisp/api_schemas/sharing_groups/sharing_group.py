from datetime import datetime

from pydantic import BaseModel, Field


class SharingGroup(BaseModel):
    id: str = Field(max_length=36)
    name: str = Field(max_length=255)
    releasability: str | None = Field(default=None, max_length=65535)
    description: str | None = Field(default=None, max_length=65535)
    uuid: str = Field(max_length=36)
    organisation_uuid: str | None = Field(default=None, max_length=36)
    org_id: str = Field(max_length=10)
    sync_user_id: str | None = Field(default=None, max_length=10)
    active: bool
    created: datetime
    modified: datetime
    local: bool
    roaming: bool
