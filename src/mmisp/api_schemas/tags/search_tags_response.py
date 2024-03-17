from pydantic import BaseModel

from mmisp.api_schemas.tags.get_tag_response import TagAttributesResponse
from mmisp.api_schemas.taxonomies.export_taxonomies_response import TaxonomyPredicateSchema
from mmisp.api_schemas.taxonomies.get_taxonomy_response import TaxonomyView


class TaxonomyPredicateResponse(TaxonomyPredicateSchema):
    id: str
    taxonomy_id: str
    colour: str
    exclusive: bool
    numerical_value: int


class TagCombinedModel(BaseModel):
    Tag: TagAttributesResponse
    Taxonomy: TaxonomyView
    TaxonomyPredicate: TaxonomyPredicateResponse


class TagSearchResponse(BaseModel):
    response: list[TagCombinedModel]

    class Config:
        orm_mode = True
