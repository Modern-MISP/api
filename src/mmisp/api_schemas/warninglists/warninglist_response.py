from enum import Enum

from pydantic import BaseModel, Field


class Type(Enum):
    CIDR = "cidr"
    HOSTNAME = "hostname"
    STRING = "string"
    SUBSTRING = "substring"
    REGEX = "regex"


class Category(Enum):
    FALSE_POSITIVE = "False positive"
    KNOWN_IDENTIFIER = "Known identifier"


# TODO: int or str, ids?
class WarninglistEntryResponse(BaseModel):
    id: str
    value: str = Field(max_length=65535)
    warninglist_id: str
    comment: str = Field(max_length=65535)


class WarninglistResponse(BaseModel):
    id: int
    name: str = Field(max_length=255)
    type: str
    description: str = Field(max_length=65535)
    version: int
    enabled: bool
    default: bool
    category: str
    warninglist_entry_count: int
    WarninglistEntry: list[WarninglistEntryResponse] | None = None

    class Config:
        orm_mode = True
