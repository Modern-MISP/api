from typing import Any, Dict, Optional

from pydantic import BaseModel, validator

from mmisp.api_schemas.attributes.add_attribute_body import AddAttributeBody

# class ObjectCreateRequirementBody(BaseModel):
#     requirement: list[str] | None = None
#     requirement_type: list[str] | None = None


class ObjectCreateBody(BaseModel):
    name: str
    description: str
    meta_category: str
    distribution: str
    update_template_available: bool | None = None
    action: str | None = None
    template_name: str | None = None
    template_version: str | None = None
    template_description: str | None = None
    # requirements: list[ObjectCreateRequirementBody] | None = None
    sharing_group_id: int | None = None
    comment: str | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    attributes: list[AddAttributeBody] | None = None

    @validator("sharing_group_id", always=True)
    def check_sharing_group_id(cls, value: Any, values: Dict[str, Any], **kwargs: Any) -> Optional[int]:  # noqa: ANN101
        """
        If distribution equals 4, sharing_group_id will be displayed.
        """
        distribution = values.get("distribution", None)
        if distribution == "4" and value is not None:
            return value
        return None

    class Config:
        orm_mode = True
