from typing import List, Union

from . import Events
from . import Objects
from . import Tags
from fastapi import FastAPI
from pydantic import BaseModel


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


app = FastAPI()


@app.post("/attributes/restSearch")
async def attributes_reastSearch() -> (
    Union[Attributes, Events.Events, Objects.Objects, Tags.Tags]
):
    return {Attributes(), Events.Events(), Objects.Objects(), Tags.Tags()} - {
        Attributes.value1,
        Attributes.value2,
        Attributes.event_uuid,
        Attributes.AttributeTag,
    }


@app.post("/attributes/add/{eventId}")
@app.post("/attributes/{eventId}")
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


@app.put("/attributes/edit/{attributeId}")
@app.put("/attributes/{attributeId}")
async def attributes_put(
    category: str,
    value: str,
    to_ids: bool,
    distribution: str,
    comment: str,
    disable_correlation: bool,
) -> {Attributes}:
    return {Attributes} - {Attributes.AttributeTag}


@app.delete("/attributes/delete/{attributeId}")
@app.delete("/attributes/{attributeID}")
async def attributes_delete() -> str:
    return "message: Attribute deleted."


@app.post("/attributes/deleteSelected/{event_id}")
async def attributes_deleteSelected(
    id: str, event_id: str, allow_hard_delete: bool
) -> str:
    return (
        '"saved": true,'
        + '"success": true,'
        + '"name": "1 attribute deleted.",'
        + '"message": "1 attribute deleted.",'
        + '"url": "/attributes/deleteSelected/{event_id}",'
        + '"id": "{event_id}"'
    )


@app.post("/attributes/restore/{attributeId}")
async def attributes_restore() -> {Attributes}:
    return {Attributes} - {Attributes.AttributeTag}


@app.post("/attributes/addTag/{attributeId}/{tagId}/local:{local}")
async def attributes_addTag() -> str:
    return '"saved": true,' + '"success": "Tag added.",' + '"check_publish": true'


@app.post("/attributes/removeTag/{attributeId}/{tagId}")
async def attributes_removeTag() -> str:
    return '"saved": true,' + '"success": "Tag removed.",' + '"check_publish": true'


@app.get("/attributes")
async def attributes_get() -> {Attributes}:
    return {Attributes} - {Attributes.event_uuid, Attributes.AttributeTag}


@app.get("/attributes/view/{attributeId}")
@app.get("/attributes/{attributeId}")
async def attributes_getSpecifiedAttribute() -> {Attributes}:
    return {Attributes} - {Attributes.value1, Attributes.value2}


@app.get("/attributes/attributeStatistics/{context}/{percentage}")
async def attributes_statistics() -> str:
    return (
        '"[Type/Category]": "[Count/Percentage of attributes with this type/category]"'
    )


@app.get("/attributes/describeTypes")
async def attributes_describeTypes() -> str:
    return "[List all attribute categories and types]"
