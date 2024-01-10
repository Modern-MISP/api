from pydantic import BaseModel


class Count:
    total_count: int = -1
    current_count: int = -1


class TaxonomyViewSchema(BaseModel):
    id: str = ""
    namespace: str = ""
    description: str = ""
    version: str = ""
    enabled: bool = False
    exclusive: bool = False
    required: bool = False
    highlighted: bool = False
    count: Count = Count()

    class Config:
        orm_mode = True

