from pydantic import BaseModel


class Data(BaseModel):
    scope: list[str]
    field: list[str]
    value: list[str]
    tags: list[str]
    message: str


class NoticelistEntry(BaseModel):
    id: int
    noticelistId: int
    data: Data


class Noticelist(BaseModel):
    id: int
    name: str
    expanded_name: str
    ref: str
    geographical_area: str
    version: int
    enabled: bool
    NoticelistEntry: list[NoticelistEntry]

    class Config:
        orm_mode = True
