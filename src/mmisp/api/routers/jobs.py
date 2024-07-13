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
from mmisp.api_schemas.jobs import (
    AddAttributeViaFreeTextImportEventBody,
    AddAttributeViaFreeTextImportEventResponse,
    FreeTextImportWorkerBody,
    FreeTextImportWorkerData,
    FreeTextImportWorkerUser,
    FreeTextProcessID,
    ProcessFreeTextResponse,
    AttributeType
)
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
        response = await client.get(f"{config.WORKER_URL}/jobs/{id}/status")
    return response.json()


@router.post("/jobs/freeTextImport",
    status_code=status.HTTP_200_OK,
    response_model=FreeTextProcessID,
    summary="start the freetext import process via worker",
)
async def start_freeTextImport(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    body: AddAttributeViaFreeTextImportEventBody,
) -> FreeTextProcessID:
    """Starts the freetext import process by submitting the freetext to the worker.

    Input:

    - the user's authentification status

    - the body of the freetext

    Output:

    - dict
    """
    body_dict = body.dict()
    user = FreeTextImportWorkerUser(user_id=auth.user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no user")
    
    data = FreeTextImportWorkerData(data=body_dict["Attribute"]["value"])
    worker_body = FreeTextImportWorkerBody(user=user, data=data).dict()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{config.WORKER_URL}/job/processFreeText", json=worker_body)

    response_data = response.json()
    job_id = response_data["job_id"]

    return FreeTextProcessID(id=job_id)


@router.get("/jobs/freeTextImport/{jobid}")
async def get_freetext_job(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    job_id: Annotated[str, Path(alias="jobid")],
) -> ProcessFreeTextResponse:
    """If completed, returns the freetext import response, if not, it returns a hhtp exception.

    Input:

    - the user's authentification status

    - the current database

    - the event id

    - the job id

    Output:

    - the processed data to be viewed and selected by the user
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

    result = response.json()
    parsed_response = ProcessFreeTextResponse.parse_obj(result)

    return parsed_response


@router.post(
    "/jobs/freeTextImport/{eventID}",
    status_code=status.HTTP_200_OK,
    summary="Start the freetext import process via worker",
)
async def start_freetext_import(
    event_id: Annotated[str, Path(alias="eventID")],
    body: ProcessFreeTextResponse,
    db: Annotated[Session, Depends(get_db)]
) -> list[AddAttributeViaFreeTextImportEventResponse]:
    """Adds the Attributes the user has selected

    Input:

    - the current database

    - the event id

    - the selected Attributes

    Output:

    - the processed data to be viewed and selected by the user
    """
    return await _add_attribute_via_free_text_import(db, event_id, body)


# --- endpoint logic ---


async def _add_attribute_via_free_text_import(
    db: Session, event_id: str, body: ProcessFreeTextResponse
) -> list[AddAttributeViaFreeTextImportEventResponse]:
    event: Event | None = await db.get(Event, event_id)

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    response_list = []

    for attribute in body.attributes:
        value = attribute.value
        attribute_type = attribute.default_type
        category = GetDescribeTypesAttributes().sane_defaults[attribute_type]["default_category"].value
        
        value1, value2 = value, ""

        new_attribute = Attribute(event_id=event_id, value1=value1, value2=value2, type=attribute_type, category=category)

        db.add(new_attribute)

        await db.commit()

        attribute_response_dict = new_attribute.__dict__.copy()
        attribute_response_dict["value"] = new_attribute.value1
        attribute_response_dict["original_value"] = new_attribute.value1
        response_list.append(AddAttributeViaFreeTextImportEventResponse(**attribute_response_dict))

    return response_list

