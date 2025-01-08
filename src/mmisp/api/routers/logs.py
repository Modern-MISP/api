from typing import Annotated, Any, List, Sequence

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy import desc, select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.logs import LogsRequest
from mmisp.db.database import Session, get_db
from mmisp.db.lib import get_count_from_select
from mmisp.db.models.log import Log
from mmisp.lib.logger import alog, log
from mmisp.workflows.fastapi import log_to_json_dict

router = APIRouter(tags=["logs"])


@router.get(
    "/logs/index",
    status_code=status.HTTP_200_OK,
    summary="List logs",
)
@alog
async def logs_index_get(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    response: Response,
    page: int | None = None,
    limit: int | None = None,
    model: str | None = None,
    action: str | None = None,
    model_id: str | None = None,
) -> List[Any]:
    """
    List logs, filter can be applied.

    - **page** the page for pagination
    - **limit** the limit for pagination
    """
    request = LogsRequest(
        model=model,
        action=action,
        model_id=model_id,
    )

    if page is not None:
        request.page = page
    if limit is not None:
        request.limit = limit

    count, logs = await query_logs(request, db)
    response.headers["X-Result-Count"] = str(count)
    return transform_logs_to_response(logs)


@router.post(
    "/logs/index",
    status_code=status.HTTP_200_OK,
    summary="List logs",
)
@alog
async def logs_index_post(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    request: LogsRequest,
    response: Response,
) -> List[Any]:
    """
    List logs, filter can be applied.

    - **model** the source for the log creation (f.e. 'User', 'Workflow', 'AuthKey', ...)
    - **action** the action in which the log was created
    - **model_id** the id of the model
    - **page** the page for pagination
    - **limit** the limit for pagination
    """
    count, logs = await query_logs(request, db)
    response.headers["X-Result-Count"] = str(count)
    return transform_logs_to_response(logs)


@log
def transform_logs_to_response(logs: Sequence[Log]) -> List[Any]:
    result = []

    for log_entry in logs:
        log_json = log_to_json_dict(log_entry)
        result.append(log_json)

    return result


@alog
async def query_logs(request: LogsRequest, db: Session) -> tuple[int, Sequence[Log]]:
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

    count = await get_count_from_select(db, query)
    return count, db_result.scalars().all()


@router.get(
    "/logs/index/{logId}",
    status_code=status.HTTP_200_OK,
    summary="Get single log",
)
@alog
async def log_by_id(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    log_id: Annotated[int, Path(alias="logId")],
) -> dict:
    log = await db.get(Log, log_id)
    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"message": f"Could not a log with id {log_id}"}
        )
    return log_to_json_dict(log)
