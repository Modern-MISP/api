import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from starlette import status

from mmisp.db.database import Session, get_db
from mmisp.db.models.event import Event
from mmisp.lib.logger import alog

logger = logging.getLogger("mmisp")
router = APIRouter(tags=["test"])


@router.get(
    "/test_logging",
    status_code=status.HTTP_200_OK,
)
@alog
async def test_logging(
    db: Annotated[Session, Depends(get_db)],
) -> str:
    logger.info("hello")
    r = await db.execute(select(Event).filter(Event.id == 2))
    print(r.scalars().all())
    await asyncio.sleep(5)
    logger.info("from the other side")
    return "blub"


@router.get(
    "/test_logging_error",
    status_code=status.HTTP_200_OK,
)
@alog
async def test_logging_error() -> str:
    logger.info("hello")
    raise ValueError("testing")


@router.get(
    "/test_sublogger",
    status_code=status.HTTP_200_OK,
)
@alog
async def test_sublogger() -> str:
    workflow_logger = logging.getLogger("mmisp.workflow")
    workflow_logger.setLevel(logging.DEBUG)
    workflow_logger.debug("hello workflow logger")
    logger.debug("this should not be there")
    return "this"
