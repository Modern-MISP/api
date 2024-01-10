from pydantic import BaseModel


class TaxonomyAbleSchema(BaseModel):
    id: str
    saved: bool
    success: bool
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True
