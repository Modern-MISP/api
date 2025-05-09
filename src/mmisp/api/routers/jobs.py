import json
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException

from mmisp.api.auth import Auth, AuthStrategy, authorize
from mmisp.api.config import config
from mmisp.lib.logger import alog

router = APIRouter(tags=["jobs"])


@router.get("/jobs/{job_type}/{id}")
@alog
async def get_job(  # noqa
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    job_type: str,
    id: str,
    # ) -> dict:
):
    """Gets a job.

    Args:
      auth: the user's authentification status
      id: the job id
    Returns:
      the job result
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{config.WORKER_URL}/job/{job_type}/{id}", headers={"Authorization": f"Bearer {config.WORKER_KEY}"}
        )

    if response.status_code == 409:
        raise HTTPException(status_code=409, detail="Job is not yet finished. Please try again in a few seconds")
    elif response.status_code == 204:
        raise HTTPException(status_code=204, detail="Job has no result")
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail="Job does not exist")
    elif response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")
    try:
        data = response.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="ERROR -- JSON from Worker API was not parsable")

    return data
