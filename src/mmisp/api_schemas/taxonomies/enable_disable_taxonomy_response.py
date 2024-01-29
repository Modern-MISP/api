from pydantic import BaseModel


class EnDisableTaxonomyResponse(BaseModel):
    id: str
    saved: bool
    success: bool
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True
