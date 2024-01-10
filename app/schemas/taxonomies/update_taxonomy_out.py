from pydantic import BaseModel


class TaxonomyUpdateSchema(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True
