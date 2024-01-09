from typing import List

from fastapi import APIRouter, Depends  # , HTTPException
from sqlalchemy.orm import Session

from ..database import get_db

# from ..models.object import Object
from ..schemas.objects.object_schema import (
    ObjectDeleteSchema,
    ObjectSchema,
    ResponseSchema,
)

router = APIRouter(prefix="/objects")


@router.post("/restsearch", response_model=List[ResponseSchema])
async def restsearch(db: Session = Depends(get_db)) -> None:
    pass


@router.post("/add/{eventId}/{objectTemplateId}", response_model=List[ObjectSchema])
@router.post("/{eventId}/{objectTemplateId}", response_model=List[ObjectSchema])
async def add_object(
    event_id: str, object_template_id: str, db: Session = Depends(get_db)
) -> None:
    pass


@router.get("/view/{objectId}", response_model=List[ObjectSchema])
@router.get("/{objectId}")
async def get_feed_details(object_id: str, db: Session = Depends(get_db)) -> None:
    pass


@router.delete(
    "/delete/{objectId}/{hardDelete}", response_model=List[ObjectDeleteSchema]
)
@router.delete("/{objectId}/{hardDelete}")
async def delete_object(
    objectId: str, hardDelete: bool, db: Session = Depends(get_db)
) -> None:
    pass
