from pydantic import BaseModel

from .search_objects_response import ObjectWithAttributesSearchResponse


class ObjectGetAddedResponse(BaseModel):
    object: ObjectWithAttributesSearchResponse

    class Config:
        orm_mode = True
