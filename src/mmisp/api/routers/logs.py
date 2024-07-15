from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from mmisp.api.auth import Auth, AuthStrategy, authorize
from mmisp.db.database import Session, get_db
from mmisp.db.models.log import Log

router = APIRouter(tags=["logs"])


@router.post(
    "/logs/index",
    status_code=status.HTTP_201_CREATED,
    summary="Add object to event",
    description="Add a new object to a specific event using a template.",
)
async def add_object(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))], db: Annotated[Session, Depends(get_db)]
) -> List[dict]:
    db_result = db.execute(select(Log).order_by(Log.created.desc()).limit(50))
    logs = db_result.scalars().all()

    pass
