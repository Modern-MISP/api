from typing import List

from pydantic import BaseModel


class Taxonomy(BaseModel):
    id: str
    namespace: str
    description: str
    version: str
    enabled: bool
    exclusive: bool
    required: bool
    highlighted: bool

    class Config:
        orm_mode = True


class TaxonomyViewSchema(BaseModel):
    id: str
    namespace: str
    description: str
    version: str
    enabled: bool
    exclusive: bool
    required: bool
    highlighted: bool
    total_count: int
    current_count: int

    class Config:
        orm_mode = True


class TaxonomyEntrySchema(BaseModel):
    id: str
    namespace: str
    description: str
    version: str
    enabled: bool
    exclusive: bool
    required: bool
    highlighted: bool
    tag: str
    expanded: str
    exclusive_predicate: bool
    description: str
    existing_tag: bool # Kann auch Tag Objekt sein, nicht zwingend bool laut Pflichtenheft. In Implementierung schauen

    class Config:
        orm_mode = True


class TaxonomyAbleSchema(BaseModel):
    id: str
    saved: bool
    success: bool
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True


class TaxonomyUpdateSchema(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str

    class Config:
        orm_mode = True


class TaxonomyPredicateSchema:
    description: str
    value: str
    expanded: str


class Entry:
    value: str
    expanded: str
    description: str


class TaxonomyValueSchema:
    predicate: str
    entries: List[Entry]


class TaxonomyExportSchema(BaseModel):
    namespace: str
    description: str
    version: int
    exclusive: bool
    predicates: List[TaxonomyPredicateSchema]
    values: List[TaxonomyValueSchema]

    class Config:
        orm_mode = True
