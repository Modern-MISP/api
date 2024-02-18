from pydantic import BaseModel


class TaxonomyPredicateSchema(BaseModel):
    value: str
    expanded: str
    description: str


class ExportTaxonomyEntry(BaseModel):
    value: str
    expanded: str
    description: str


class TaxonomyValueSchema(BaseModel):
    predicate: str
    entry: list[ExportTaxonomyEntry]


class ExportTaxonomyResponse(BaseModel):
    namespace: str
    description: str
    version: int
    exclusive: bool
    predicates: list[TaxonomyPredicateSchema]
    values: list[TaxonomyValueSchema]

    class Config:
        orm_mode = True
