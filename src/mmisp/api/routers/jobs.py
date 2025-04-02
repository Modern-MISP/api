from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api.config import config
from mmisp.lib.logger import alog

router = APIRouter(tags=["jobs"])


@router.get("/jobs/{id}")
@alog
async def get_job(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))], id: str
) -> dict:
    """Gets a job.

    args:

    - the user's authentification status

    - the id

    returns:

    - dict
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{config.WORKER_URL}/job/{id}/result", headers={"Authorization": f"Bearer {config.WORKER_KEY}"}
        )

    if response.status_code == 409:
        raise HTTPException(status_code=409, detail="Job is not yet finished. Please try again in a few seconds")
    elif response.status_code == 204:
        raise HTTPException(status_code=204, detail="Job has no result")
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail="Job does not exist")
    elif response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")

    return response.json()
