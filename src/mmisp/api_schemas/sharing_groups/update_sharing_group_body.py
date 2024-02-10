from pydantic import BaseModel, Field


class UpdateSharingGroupBody(BaseModel):
    name: str = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=65535)
    releasability: str = Field(default=None, max_length=65535)
    active: bool | None = None
    roaming: bool | None = None
    local: bool | None = None
