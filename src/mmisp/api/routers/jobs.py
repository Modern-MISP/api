from typing import Annotated

import httpx
from fastapi import APIRouter, Depends

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api.config import config

router = APIRouter(tags=["jobs"])


@router.get("/jobs/{id}")
async def get_job(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))], id: str
) -> dict:
    """Gets a job."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{config.WORKER_URL}/jobs/{id}/status")
    return response.json()
