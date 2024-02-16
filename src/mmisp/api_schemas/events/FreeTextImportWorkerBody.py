from pydantic import BaseModel


class FreeTextImportWorkerUser(BaseModel):
    user_id: int


class FreeTextImportWorkerData(BaseModel):
    data: str


class FreeTextImportWorkerBody(BaseModel):
    user: FreeTextImportWorkerUser
    data: FreeTextImportWorkerData

    class Config:
        orm_mode = True
