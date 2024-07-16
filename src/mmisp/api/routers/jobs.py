from calendar import timegm
from collections.abc import Sequence
from datetime import date
from time import gmtime
from typing import Annotated, Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.future import select
from sqlalchemy.sql import Select
from starlette import status
from starlette.requests import Request

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api.config import config

from mmisp.api_schemas.attributes import GetDescribeTypesAttributes
from mmisp.db.database import Session, get_db
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.event import Event, EventReport, EventTag
from mmisp.db.models.object import Object
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.tag import Tag
from mmisp.db.models.user import User
from mmisp.util.models import update_record
from mmisp.util.partial import partial

router = APIRouter(tags=["jobs"])


@router.get("/jobs/{id}")
async def get_job(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))], id: str
) -> dict:
    """Gets a job.

    Input:

    - the user's authentification status

    - the id

    Output:

    - dict
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{config.WORKER_URL}/jobs/{id}/result")
        
    if response.status_code == 409:
        raise HTTPException(status_code=409, detail="Job is not yet finished. Please try again in a few seconds")
    elif response.status_code == 204:
        raise HTTPException(status_code=204, detail="Job has no result")
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail="Job does not exist")
    elif response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")
    
    return response.json()

