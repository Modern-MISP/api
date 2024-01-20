from pydantic import BaseModel, Field
from enum import Enum


class Type(Enum):
    CIDR = "cidr"
    HOSTNAME = "hostname"
    STRING = "string"
    SUBSTRING = "substring"
    REGEX = "regex"


class Category(Enum):
    FALSE_POSITIVE = "False positive"
    KNOWN_IDENTIFIER = "Known identifier"


class WarninglistEntry(BaseModel):
    id: int
    value: str = Field(max_length=65535)
    warninglist_id: int
    comment: str = Field(max_length=65535)


class Warninglist(BaseModel):
    id: int
    name: str = Field(max_length=255)
    type: Type
    description: str = Field(max_length=65535)
    version: int
    enabled: bool
    default: bool
    category: Category
    warninglist_entry_count: int
    WarninglistEntry: list[WarninglistEntry]

    class Config:
        orm_mode = True
