from pydantic import BaseModel


class UpdateTaxonomyResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True
