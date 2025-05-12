import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mmisp.api.auth import Auth, AuthStrategy, authorize
from mmisp.api_schemas.object_templates import RespItemObjectTemplateIndex, RespObjectTemplateView
from mmisp.db.database import Session, get_db
from mmisp.db.models.object import ObjectTemplate
from mmisp.lib.logger import alog
from mmisp.lib.permissions import Permission

router = APIRouter(tags=["object_templates"])


@router.get(
    "/object_templates",
    summary="List all object templates",
)
@router.get(
    "/object_templates/index",
    summary="List all object templates",
)
@alog
async def index_object_templates(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, permissions=[Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> list[RespItemObjectTemplateIndex]:
    """
    Return all index object templates.

    Args:
      auth: The api authentication object
      db: The current database

    Returns:
      A list of object template indizes
    """
    return await _index_object_templates(auth=auth, db=db)


@router.get("/object_templates/view/{objectTemplateId}")
@alog
async def view_object_template(
    object_template_id: Annotated[uuid.UUID | int, Path(alias="objectTemplateId")],
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, permissions=[Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> RespObjectTemplateView:
    """
    Retrieve all information about a given object template.

    Args:
      auth: The api authentication object
      db: The database session
      object_template_id: The ID of the object template information shall be retrieved

    Returns:
      All information about the object template
    """

    return await _view_object_template(object_template_id, auth, db)


async def _index_object_templates(auth: Auth, db: AsyncSession) -> list[RespItemObjectTemplateIndex]:
    qry = select(ObjectTemplate)
    res = await db.execute(qry)

    all_object_templates = list(res.scalars().all())

    return [RespItemObjectTemplateIndex(ObjectTemplate=x.asdict()) for x in all_object_templates]


async def _view_object_template(
    object_template_id: uuid.UUID | int, auth: Auth, db: AsyncSession
) -> RespObjectTemplateView:
    qry = (
        select(ObjectTemplate).order_by(ObjectTemplate.version).limit(1).options(selectinload(ObjectTemplate.elements))
    )
    if isinstance(object_template_id, uuid.UUID):
        qry = qry.filter(ObjectTemplate.uuid == object_template_id)
    else:
        qry = qry.filter(ObjectTemplate.id == object_template_id)

    res = await db.execute(qry)

    object_template = res.scalars().one_or_none()

    if object_template is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    elements = [x.asdict() for x in object_template.elements]

    return RespObjectTemplateView(ObjectTemplate=object_template.asdict(), ObjectTemplateElement=elements)
