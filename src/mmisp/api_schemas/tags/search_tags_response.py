from pydantic import BaseModel

from ..taxonomies.get_taxonomy_out import TaxonomyView
from .get_tag_response import TagAttributesResponse


# TODO: Import from schemas/taxonomie directly
class TaxonomyPredicateResponse(BaseModel):
    id: str
    taxonomy_id: str
    value: str
    expanded: str
    colour: str
    description: str
    exclusive: bool
    numerical_value: int


class TagCombinedModel(BaseModel):
    Tag: TagAttributesResponse
    Taxonomy: TaxonomyView
    TaxonomyPredicate: TaxonomyPredicateResponse


class TagSearchResponse(BaseModel):
    root: list[TagCombinedModel]

    class Config:
        orm_mode = True
