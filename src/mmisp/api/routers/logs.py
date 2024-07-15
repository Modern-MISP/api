from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from mmisp.api.auth import Auth, AuthStrategy, authorize
from mmisp.api_schemas.logs import LogsRequest
from mmisp.db.database import Session, get_db
from mmisp.db.models.log import Log
from mmisp.workflows.fastapi import log_to_json_dict

router = APIRouter(tags=["logs"])


@router.post(
    "/admin/logs/index",
    status_code=status.HTTP_201_CREATED,
    summary="Add object to event",
    description="Add a new object to a specific event using a template.",
)
async def add_object(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    request: LogsRequest,
) -> List[Any]:
    logs = await query_logs(request, db)

    result = []

    for log in logs:
        log_json = log_to_json_dict(log)
        result.append(log_json)

    return result


async def query_logs(request: LogsRequest, db: Session) -> List[Log]:
    query = select(Log)

    if request.model:
        query = query.filter(Log.model == request.model)
    if request.action:
        query = query.filter(Log.action == request.action)
    if request.model_id:
        query = query.filter(Log.model_id == request.model_id)

    query = query.offset((request.page - 1) * request.limit).limit(request.limit)
    query = query.order_by(Log.created.desc())

    db_result = await db.execute(query)
    return db_result.scalars().all()
