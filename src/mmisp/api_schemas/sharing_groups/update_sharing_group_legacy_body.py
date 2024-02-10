from datetime import datetime

from pydantic import BaseModel, Field


class UpdateSharingGroupLegacyBody(BaseModel):
    id: str | None = None
    """attribute will be ignored"""
    uuid: str | None = Field(default=None, max_length=36)
    """attribute will be ignored"""
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=65535)
    releasability: str | None = Field(default=None, max_length=65535)
    local: bool | None = None
    active: bool | None = None
    org_count: str | None = None
    """attribute will be ignored"""
    organisation_uuid: str | None = Field(default=None, max_length=36)
    """attribute will be ignored"""
    org_id: str | None = Field(default=None, max_length=10)
    """attribute will be ignored"""
    sync_user_id: str | None = Field(default=None, max_length=10)
    """attribute will be ignored"""
    created: datetime | None = None
    """attribute will be ignored"""
    modified: datetime | None = None
    """attribute will be ignored"""
    roaming: bool | None = None
