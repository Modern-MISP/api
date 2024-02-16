from pydantic import BaseModel


class Data(BaseModel):
    scope: str | list[str] | None
    field: str | list[str] | None
    value: str | list[str] | None
    tags: str | list[str] | None
    message: str


class NoticelistEntryResponse(BaseModel):
    id: int
    noticelistId: int
    data: Data


class NoticelistResponse(BaseModel):
    id: int
    name: str
    expanded_name: str
    ref: str
    geographical_area: str
    version: int
    enabled: bool
    NoticelistEntry: list[NoticelistEntryResponse]

    class Config:
        orm_mode = True
