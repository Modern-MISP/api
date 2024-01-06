from pydantic import BaseModel
from typing import List, Union
from fastapi import APIRouter
from . import Events
from . import Objects
from . import Tags


class Attributes(BaseModel):
    id: str = ""
    event_id: str = ""
    object_id: str = ""
    object_relation: str = ""
    category: str = ""
    type: str = ""
    value: str = ""
    value1: str = ""
    value2: str = ""
    to_ids: bool = True
    uuid: str = ""
    timestamp: str = ""
    distribution: str = ""
    sharing_group_id: str = ""
    comment: str = ""
    deleted: bool = False
    disable_correlation: bool = False
    first_seen: str = ""
    last_seen: str = ""
    event_uuid: str = ""
    AttributeTag: List[str] = [""]


router = APIRouter(prefix="/attributes")


@router.post("/restSearch")
async def attributes_reastSearch() -> (
    Union[Attributes, Events.Events, Objects.Objects, Tags.Tags]
):
    return {Attributes(), Events.Events(), Objects.Objects(), Tags.Tags()} - {
        Attributes.value1,
        Attributes.value2,
        Attributes.event_uuid,
        Attributes.AttributeTag,
    }


@router.post("/add/{eventId}")
@router.post("/{eventId}")
async def attributes_post(
    value: str,
    type: str,
    category: str,
    to_ids: bool,
    distribution: str,
    comment: str,
    disable_correlation: bool,
) -> {Attributes}:
    return {Attributes} - {Attributes.event_uuid}


@router.put("/edit/{attributeId}")
@router.put("/{attributeId}")
async def attributes_put(
    category: str,
    value: str,
    to_ids: bool,
    distribution: str,
    comment: str,
    disable_correlation: bool,
) -> {Attributes}:
    return {Attributes} - {Attributes.AttributeTag}


@router.delete("/delete/{attributeId}")
@router.delete("/{attributeID}")
async def attributes_delete() -> str:
    return "message: Attribute deleted."


@router.post("/deleteSelected/{event_id}")
async def attributes_deleteSelected(
    id: str, event_id: str, allow_hard_delete: bool
) -> str:
    return (
        '"saved": true,'
        + '"success": true,'
        + '"name": "1 attribute deleted.",'
        + '"message": "1 attribute deleted.",'
        + '"url": "/deleteSelected/{event_id}",'
        + '"id": "{event_id}"'
    )


@router.post("/restore/{attributeId}")
async def attributes_restore() -> {Attributes}:
    return {Attributes} - {Attributes.AttributeTag}


@router.post("/addTag/{attributeId}/{tagId}/local:{local}")
async def attributes_addTag() -> str:
    return '"saved": true,' + '"success": "Tag added.",' + '"check_publish": true'


@router.post("/removeTag/{attributeId}/{tagId}")
async def attributes_removeTag() -> str:
    return '"saved": true,' + '"success": "Tag removed.",' + '"check_publish": true'


@router.get("/attributes")
async def attributes_get() -> {Attributes}:
    return {Attributes} - {Attributes.event_uuid, Attributes.AttributeTag}


@router.get("/view/{attributeId}")
@router.get("/{attributeId}")
async def attributes_getSpecifiedAttribute() -> {Attributes}:
    return {Attributes} - {Attributes.value1, Attributes.value2}


@router.get("/attributeStatistics/{context}/{percentage}")
async def attributes_statistics() -> str:
    return (
        '"[Type/Category]": "[Count/Percentage of attributes with this type/category]"'
    )


@router.get("/describeTypes")
async def attributes_describeTypes() -> str:
    return "[List all attribute categories and types]"
