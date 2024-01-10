from pydantic import BaseModel, Field

from .warninglists import Warninglist, Type, Category


class GetSelectedAllWarninglists(BaseModel):
    id: int
    name: str = Field(max_length=255)
    type: Type
    description: str = Field(max_length=65535)
    version: int
    enabled: bool
    default: bool
    category: Category
    warninglist_entry_count: int
    valid_attributes: str


class GetSelectedAllWarninglistsResponse(BaseModel):
    response: list[GetSelectedAllWarninglists]
