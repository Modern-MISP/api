from pydantic import BaseModel
from typing import Union


class TagSchema(BaseModel):
    id: str
    name: str
    colour: str
    exportable: bool
    org_id: str
    user_id: str
    hide_tag: bool
    numerical_value: str
    is_galaxy: bool
    is_custom_galaxy: bool
    inherited: Union[int, bool]

    class Config:
        orm_mode = True


class TaxonomySchema(BaseModel):
    id: str
    namespace: str
    description: str
    version: str
    enabled: bool
    exclusive: bool
    required: bool


class TaxonomyPredicateSchema(BaseModel):
    id: str
    taxonomy_id: str
    value: str
    expanded: str
    colour: str
    description: str
    exclusive: bool
    numerical_value: int


class TagDeleteSchema(BaseModel):
    name: str
    message: str
    url: str


class TagSearchSchema(BaseModel):
    Tag: TagSchema
    Taxonomy: TaxonomySchema
    TaxonomyPredicate: TaxonomyPredicateSchema
