from pydantic import BaseModel

from mmisp.db.models.attribute import Attribute


class GetDescribeTypesDescribeTypesAttributes(BaseModel):
    __attribute_types__: list[type[Attribute]] = Attribute.__subclasses__()
    sane_defaults: dict = {}
    for cls in Attribute.__subclasses__():
        sane_defaults.update(
            {
                cls.__mapper_args__["polymorphic_identity"]: {
                    "default_category": cls.default_category,
                    "to_ids": cls.to_ids,
                }
            }
        )

    types: list[str] = []
    for cls in __attribute_types__:
        types.append(cls.__mapper_args__["polymorphic_identity"])

    categories: list[str] = []
    for cls in __attribute_types__:
        for __category__ in cls.categories:
            if __category__ not in categories:
                categories.append(__category__)

    category_type_mappings: dict = {}
    # iterate over all elements of the list "categories"
    for __category__ in categories:
        __types_mapped_to_category__: list[str] = []
        # iterate over all AttributeTypes
        for cls in __attribute_types__:
            # iterate over all elements of the list "categories" in the current subclass
            for __attribute_category__ in cls.categories:
                # check if element in "categories" (subclass) equals to current category
                if __attribute_category__ == __category__:
                    __types_mapped_to_category__.append(cls.__mapper_args__["polymorphic_identity"])
                    category_type_mappings.update({__attribute_category__: __types_mapped_to_category__})


class GetDescribeTypesResponse(BaseModel):
    result: GetDescribeTypesDescribeTypesAttributes

    class Config:
        orm_mode = True
