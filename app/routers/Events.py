from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.attribute import Attribute, ShadowAttribute
from ..models.event import Event, EventReport
from ..models.galaxy import Galaxy
from ..models.object import Object
from ..models.tag import Tag
from app.schemas.attributes.attribute_schema import AttributeSchema
from schemas.event_schema import EventSchema


router = APIRouter(prefix="/events", tags=["events"])


# -- Delete


@router.delete("/delete/{eventId}", response_model=str)
@router.delete("/{eventId}", response_model=str)
async def events_delete(db: Session = Depends(get_db)) -> str:
    return ""


# -- Get


@router.get("/", response_model=List[EventSchema])
async def events_get(db: Session = Depends(get_db)) -> List[Event]:
    return []


@router.get("/view/{eventId}", response_model=EventSchema)
@router.get("/{eventId}", response_model=EventSchema)
async def events_getById(db: Session = Depends(get_db)) -> Event:
    return Event


# -- Post


# ObjectReference[] missing
@router.post("/restSearch", response_model=List[EventSchema])
async def events_restSearch(db: Session = Depends(get_db)) -> List[Event]:
    return Attribute, Event, EventReport, Object, Tag
    """
    return {
        Events(),
        attributes.Attributes(),
        EventReport.EventReport(),
        objects.Objects(),
        tags.Tags(),
    } - {Events.sighting_timestamp, tags.org_id, tags.inherited}
    """


@router.post("/add", response_model=EventSchema)
@router.post("/", response_model=EventSchema)
async def events_post(db: Session = Depends(get_db)) -> Event:
    return Event
    """
    return {Events, organisations.local} - {Events.sighting_timestamp}
    """


@router.post("/index", response_model=List[EventSchema])
async def events_index(db: Session = Depends(get_db)) -> List[Event]:
    return []


@router.post("/publish/{eventId}", response_model=str)
async def events_publish(db: Session = Depends(get_db)) -> str:
    return ""


@router.post("/unpublish/{eventId}", response_model=str)
async def events_unpublish(db: Session = Depends(get_db)) -> str:
    return ""


@router.post("/addTag/{eventId}/{tagId}/local:{local}", response_model=str)
async def events_addTag(db: Session = Depends(get_db)) -> str:
    return ""


@router.post("/removeTag/{eventId}/{tagId}", response_model=str)
async def events_removeTag(db: Session = Depends(get_db)) -> str:
    return ""


@router.post("/freeTextImport/{eventId}", response_model=AttributeSchema)
async def events_freeTextImport(value: str, db: Session = Depends(get_db)) -> Attribute:
    return Attribute


# -- Put


# ObjectReference[] missing
@router.put("/edit/{eventId}", response_model=EventSchema)
@router.put("/{eventId}", response_model=EventSchema)
async def events_put(db: Session = Depends(get_db)) -> Event:
    return ShadowAttribute, Event, Galaxy, Object, Tag
    """
    return {
        Events,
        galaxies.Galaxies,
        attributes.ShadowAttribute,
        object.ObjectReference,
        tags.Tags,
    }
    """
