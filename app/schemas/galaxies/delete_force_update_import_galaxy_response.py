from pydantic import BaseModel


class DeleteForceUpdateImportGalaxyResponse(BaseModel):
    saved: bool
    succes: bool
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True
