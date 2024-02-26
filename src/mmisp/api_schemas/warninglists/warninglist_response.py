from pydantic import BaseModel, Field


class WarninglistEntryResponse(BaseModel):
    id: str
    value: str = Field(max_length=65535)
    warninglist_id: str
    comment: str = Field(max_length=65535)


class WarninglistResponse(BaseModel):
    id: str
    name: str = Field(max_length=255)
    type: str
    description: str = Field(max_length=65535)
    version: str
    enabled: bool
    default: bool
    category: str
    warninglist_entry_count: str
    WarninglistEntry: list[WarninglistEntryResponse] | None = None

    class Config:
        orm_mode = True
