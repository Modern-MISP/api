from pydantic import BaseModel


class ObjectCreateAttributesBody(BaseModel):
    category: str
    value: str
    to_ids: bool
    disable_correlation: bool
    distribution: str
    comment: str
    object_relation: str


class ObjectCreateBody(BaseModel):
    attributes: list[ObjectCreateAttributesBody]

    class Config:
        orm_mode = True
