from pydantic import BaseModel


class TaxonomyView(BaseModel):
    id: str
    namespace: str
    description: str
    version: str
    enabled: bool
    exclusive: bool
    required: bool
    highlighted: bool


class ViewTaxonomyResponse(BaseModel):
    Taxonomy: TaxonomyView
    total_count: int
    current_count: int

    class Config:
        orm_mode = True
