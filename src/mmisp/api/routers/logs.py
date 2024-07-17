from typing import Annotated, Any, List, Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy import desc, select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.logs import LogsRequest
from mmisp.db.database import Session, get_db
from mmisp.db.models.log import Log
from mmisp.workflows.fastapi import log_to_json_dict

router = APIRouter(tags=["logs"])


@router.post(
    "/logs/index",
    status_code=status.HTTP_200_OK,
    summary="List logs",
)
async def logs_index(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    request: LogsRequest,
) -> List[Any]:
    """
    List logs, filter can be applied.

    - **model** the source for the log creation (f.e. 'User', 'Workflow', 'AuthKey', ...)
    - **action** the action in which the log was created
    - **model_id** the id of the model
    """
    logs = await query_logs(request, db)

    result = []

    for log in logs:
        log_json = log_to_json_dict(log)
        result.append(log_json)

    return result


async def query_logs(request: LogsRequest, db: Session) -> Sequence[Log]:
    query = select(Log)

    if request.model:
        query = query.filter(Log.model == request.model)
    if request.action:
        query = query.filter(Log.action == request.action)
    if request.model_id:
        query = query.filter(Log.model_id == request.model_id)

    query = query.offset((request.page - 1) * request.limit).limit(request.limit)
    query = query.order_by(desc(Log.id))

    db_result = await db.execute(query)
    return db_result.scalars().all()
