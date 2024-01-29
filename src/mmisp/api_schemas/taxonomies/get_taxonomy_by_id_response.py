from pydantic import BaseModel

from mmisp.api_schemas.tags.get_tag_response import TagGetResponse


class TaxonomyEntrySchema:
    tag: str
    expanded: str
    exclusive_predicate: bool
    description: str
    existing_tag: bool | TagGetResponse  # TODO: Kann auch Tag Objekt sein, nicht zwingend bool laut Pflichtenheft?


class TaxonomyTagSchema(BaseModel):
    id: str
    namespace: str
    description: str
    version: str
    enabled: bool
    exclusive: bool
    required: bool
    highlighted: bool
    entries: list[TaxonomyEntrySchema]

    class Config:
        orm_mode = True
