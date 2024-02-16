from pydantic import BaseModel


class DeleteForceUpdateImportGalaxyResponse(BaseModel):
    saved: bool | None = None
    success: bool | None = None
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True
