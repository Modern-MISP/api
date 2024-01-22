from typing import Annotated
from mmisp.api.auth import Auth, AuthStrategy, authorize
from fastapi import APIRouter, Depends

router = APIRouter(tags=["jobs"])


@router.get("/jobs/{id}")
async def get_job(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], id: str
) -> dict:
    # query WORKER_URL/jobs/id/status
    return {}
