from datetime import datetime
from pydantic import Field, BaseModel


class UpdateSharingGroupLegacyBody(BaseModel):
    id: str | None = None
    uuid: str | None = Field(default=None, max_length=36)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=65535)
    releasability: str | None = Field(default=None, max_length=65535)
    local: bool | None = None
    active: bool | None = None
    org_count: str | None = None  # attribute will be ignored
    organisation_uuid: str | None = Field(default=None, max_length=36)
    org_id: str | None = Field(default=None, max_length=10)
    sync_user_id: str | None = Field(default=None, max_length=10)
    created: datetime | None = None
    modified: datetime | None = None
    roaming: bool | None = None
