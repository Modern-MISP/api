from pydantic import BaseModel, Field


class CreateSharingGroupBody(BaseModel):
    uuid: str | None = None
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=65535)
    releasability: str = Field(max_length=65535)
    organisation_uuid: str | None = Field(default=None, max_length=36)
    active: bool | None = None
    roaming: bool | None = None
    local: bool | None = None
