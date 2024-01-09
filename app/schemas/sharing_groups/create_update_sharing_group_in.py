from pydantic import Field, BaseModel


class CreateUpdateSharingGroupIn(BaseModel):
    uuid: str | None = Field(default=None, max_length=36)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=65535)
    releasability: str = Field(max_length=65535)
    organisation_uuid: str | None = Field(default=None, max_length=36)
    active: bool | None = None
    roaming: bool | None = None
    # local: bool  # why did I omit this in pflichtenheft?
