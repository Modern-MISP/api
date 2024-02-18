from pydantic import BaseModel


class TaxonomyPredicateSchema(BaseModel):
    description: str
    value: str
    expanded: str


class Entry(BaseModel):
    value: str
    expanded: str
    description: str


class TaxonomyValueSchema(BaseModel):
    predicate: str
    entries: list[Entry]


class ExportTaxonomyResponse(BaseModel):
    namespace: str
    description: str
    version: int
    exclusive: bool
    predicates: list[TaxonomyPredicateSchema]
    values: list[TaxonomyValueSchema]

    class Config:
        orm_mode = True
