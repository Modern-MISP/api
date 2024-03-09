from typing import Any

from pydantic import BaseModel


class Data(BaseModel):
    scope: str | list[str] | None
    field: str | list[str] | None
    value: str | list[str] | None
    tags: str | list[str] | None
    message: str | Any  # TODO: right format??


class NoticelistEntryResponse(BaseModel):
    id: int
    noticelistId: int
    data: Data


class NoticelistAttributesResponse(BaseModel):
    id: int
    name: str
    expanded_name: str
    ref: list[str]
    geographical_area: list[str]
    version: int
    enabled: bool


class NoticelistResponse(NoticelistAttributesResponse):
    NoticelistEntry: list[NoticelistEntryResponse]

    class Config:
        orm_mode = True
