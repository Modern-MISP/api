from pydantic import BaseModel, Field


class WarninglistEntryResponse(BaseModel):
    id: str
    value: str = Field(max_length=65535)
    warninglist_id: str
    comment: str | None = None


class WarninglistTypeResponse(BaseModel):
    id: str
    type: str
    warninglist_id: str


class WarninglistBaseResponse(BaseModel):
    id: str
    name: str = Field(max_length=255)
    type: str
    description: str = Field(max_length=65535)
    version: str
    enabled: bool
    default: bool
    category: str


class WarninglistAttributes(WarninglistBaseResponse):
    warninglist_entry_count: str
    valid_attributes: str


class WarninglistAttributesResponse(WarninglistBaseResponse):
    WarninglistEntry: list[WarninglistEntryResponse] | None = None
    WarninglistType: list[WarninglistTypeResponse] | None = None


class WarninglistResponse(BaseModel):
    Warninglist: WarninglistAttributesResponse

    class Config:
        orm_mode = True
