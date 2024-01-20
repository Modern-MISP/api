from pydantic import BaseModel


class TaxonomyView(BaseModel):
    id: str = ""
    namespace: str = ""
    description: str = ""
    version: str = ""
    enabled: bool = False
    exclusive: bool = False
    required: bool = False
    highlighted: bool = False


class TaxonomyViewSchema(BaseModel):
    taxonomy: TaxonomyView
    total_count: int = -1
    current_count: int = -1

    class Config:
        orm_mode = True

