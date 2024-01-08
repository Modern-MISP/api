from pydantic import BaseModel
from typing import List, Union
from fastapi import APIRouter
from . import attributes, galaxies, objects, organisations, tags


class Events(BaseModel):
    id: str = ""
    org_id: str = ""  # owner org
    distribution: str = ""
    orgc_id: str = ""  # creator org
    uuid: str = ""
    date: str = ""
    published: bool = False
    analysis: str = ""
    attribute_count: str = ""
    timestamp: str = ""
    sharing_group_id: str = ""
    proposal_email_lock: bool
    locked: bool
    threat_level_id: str = ""
    publish_timestamp: str = ""
    sighting_timestamp: str = ""
    disable_correlation: bool = False
    extends_uuid: str = ""
    event_creator_email: str = ""
    protected: str = ""
    chryprographicKey: List[str] = [""]


class EventReport(BaseModel):
    id: str = ""
    uuid: str = ""
    event_id: str = ""
    name: str = ""
    content: str = ""
    distribution: str = ""
    sharing_group_id: str = ""
    timestamp: str = ""
    deleted: bool


router = APIRouter(prefix="/events")


# ObjectReference[] missing
@router.post("/restSearch")
async def events_restSearch() -> (
    Union[
        Events,
        attributes.Attributes,
        EventReport.EventReport,
        objects.Objects,
        tags.Tags,
    ]
):
    return {
        Events(),
        attributes.Attributes(),
        EventReport.EventReport(),
        objects.Objects(),
        tags.Tags(),
    } - {Events.sighting_timestamp, tags.org_id, tags.inherited}


@router.post("/add")
@router.post("")
async def events_post() -> {Events, organisations}:
    return {Events, organisations.local} - {Events.sighting_timestamp}


# ObjectReference[] missing
@router.put("/edit/{eventId}")
@router.put("/{eventId}")
async def events_put() -> (
    {Events, galaxies.Galaxies, attributes.ShadowAttribute, tags.Tags}
):
    return {
        Events,
        galaxies.Galaxies,
        attributes.ShadowAttribute,
        object.ObjectReference,
        tags.Tags,
    }


@router.delete("/delete/{eventId}")
@router.delete("/{eventId}")
async def events_delete():
    return


@router.get("")
async def events_get():
    return


@router.post("/index")
async def events_index():
    return


@router.get("/view/{eventId}")
@router.get("/{eventId}")
async def events_getById():
    return


@router.post("/publish/{eventId}")
async def events_publish():
    return


@router.post("/unpublish/{eventId}")
async def events_unpublish():
    return


@router.post("/addTag/{eventId}/{tagId}/local:{local}")
async def events_addTag():
    return


@router.post("/removeTag/{eventId}/{tagId}")
async def events_removeTag():
    return


@router.post("/freeTextImport/{eventId}")
async def events_freeTextImport():
    return
