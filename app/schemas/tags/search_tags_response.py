from pydantic import BaseModel

from .get_tag_response import TagAttributesResponse


class TaxonomyResponse(BaseModel):
    id: str
    namespace: str
    description: str
    version: str
    enabled: bool
    exclusive: bool
    required: bool


class TaxonomyPredicateResponse(BaseModel):
    id: str
    taxonomy_id: str
    value: str
    expanded: str
    colour: str
    description: str
    exclusive: bool
    numerical_value: int


class CombinedModel(BaseModel):
    Tag: TagAttributesResponse
    Taxonomy: TaxonomyResponse  # TODO: Import from schemas/taxonomie directly
    TaxonomyPredicate: TaxonomyPredicateResponse  # TODO: Import from schemas/taxonomie directly


class TagSearchResponse(BaseModel):
    root: list[CombinedModel]

    class Config:
        orm_mode = True
