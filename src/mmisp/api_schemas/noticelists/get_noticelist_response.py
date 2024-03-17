from typing import Any

from pydantic import BaseModel


class Data(BaseModel):
    scope: str | list[str] | None
    field: str | list[str] | None
    value: str | list[str] | None
    tags: str | list[str] | None
    message: str | Any


class NoticelistEntryResponse(BaseModel):
    id: str
    noticelist_id: str
    data: Data


class NoticelistAttributes(BaseModel):
    id: str
    name: str
    expanded_name: str
    ref: list[str]
    geographical_area: list[str]
    version: str
    enabled: bool


class NoticelistAttributesResponse(NoticelistAttributes):
    NoticelistEntry: list[NoticelistEntryResponse]


class NoticelistResponse(BaseModel):
    Noticelist: NoticelistAttributesResponse

    class Config:
        orm_mode = True
