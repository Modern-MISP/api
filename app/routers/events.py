from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.attribute import Attribute
from ..models.event import Event
from schemas.attribute_schema import AttributeSchema
from schemas.event_schema import EventSchema


router = APIRouter(prefix="/events")


# ObjectReference[] missing
@router.post("/restSearch", response_model=List[EventSchema])
async def events_restSearch(db: Session = Depends(get_db)) -> List[Event]:
    pass
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
@router.post("", response_model=EventSchema)
async def events_post(db: Session = Depends(get_db)) -> Event:
    pass
    """
    return {Events, organisations.local} - {Events.sighting_timestamp}
    """


# ObjectReference[] missing
@router.put("/edit/{eventId}", response_model=EventSchema)
@router.put("/{eventId}", response_model=EventSchema)
async def events_put(db: Session = Depends(get_db)) -> Event:
    pass
    """
    return {
        Events,
        galaxies.Galaxies,
        attributes.ShadowAttribute,
        object.ObjectReference,
        tags.Tags,
    }
    """


@router.delete("/delete/{eventId}", response_model=str)
@router.delete("/{eventId}", response_model=str)
async def events_delete(db: Session = Depends(get_db)) -> str:
    pass


@router.get("", response_model=List[EventSchema])
async def events_get(db: Session = Depends(get_db)) -> List[Event]:
    pass


@router.post("/index", response_model=List[EventSchema])
async def events_index(db: Session = Depends(get_db)) -> List[Event]:
    pass


@router.get("/view/{eventId}", response_model=EventSchema)
@router.get("/{eventId}", response_model=EventSchema)
async def events_getById(db: Session = Depends(get_db)) -> Event:
    pass


@router.post("/publish/{eventId}", response_model=str)
async def events_publish(db: Session = Depends(get_db)) -> str:
    pass


@router.post("/unpublish/{eventId}", response_model=str)
async def events_unpublish(db: Session = Depends(get_db)) -> str:
    pass


@router.post("/addTag/{eventId}/{tagId}/local:{local}", response_model=str)
async def events_addTag(db: Session = Depends(get_db)) -> str:
    pass


@router.post("/removeTag/{eventId}/{tagId}", response_model=str)
async def events_removeTag(db: Session = Depends(get_db)) -> str:
    pass


@router.post("/freeTextImport/{eventId}", response_model=AttributeSchema)
async def events_freeTextImport(value: str, db: Session = Depends(get_db)) -> Attribute:
    pass
