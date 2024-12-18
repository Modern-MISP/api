from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api.config import config
from mmisp.api_schemas.worker import (
    GetWorkerJobqueue,
    GetWorkerJobs,
    GetWorkerReturningJobs,
    GetWorkerWorkers,
    RemoveAddQueueToWorker,
)

router = APIRouter(tags=["worker"])


@router.post("/worker/pause/{id}")
async def pause_workers(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))], id: str, response: Response
) -> None:
    """
    Pauses all workers.

    Args:
        auth (Auth): The user's authentication status.
        id (str): The id of the worker.

    Raises:
        HTTPException: If an error occurs while pausing the workers.
    """
    async with httpx.AsyncClient() as client:
        api_response = await client.post(
            f"{config.WORKER_URL}/worker/pause/{id}", headers={"Authorization": f"Bearer {config.WORKER_KEY}"}
        )

    response.status_code = api_response.status_code
    response.headers["x-worker-name-header"] = api_response.headers[
        "x-worker-name-header"
    ]  # possible to use an attribute but i am lazy feel free to change
    if api_response.status_code == 404:
        raise HTTPException(status_code=404, detail="Name of worker is not valid")
    elif api_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@router.post("/worker/unpause/{id}")
async def unpause_workers(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))], id: str, response: Response
) -> None:
    """
    Unpauses all workers.

    Args:
        auth (Auth): The user's authentication status.
        id (str): The id of the worker.

    Raises:
        HTTPException: If an error occurs while unpausing the workers.
    """
    async with httpx.AsyncClient() as client:
        api_response = await client.post(
            f"{config.WORKER_URL}/worker/unpause/{id}", headers={"Authorization": f"Bearer {config.WORKER_KEY}"}
        )

    response.status_code = api_response.status_code

    response.headers["x-worker-name-header"] = api_response.headers["x-worker-name-header"]
    # possible to use an attribute but i am lazy feel free to change
    # if so dont forget to delete the header in main.py
    if api_response.status_code == 404:
        raise HTTPException(status_code=404, detail="Name of worker is not valid")
    elif api_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@router.post("/worker/addQueue/{id}")
async def add_queue(
    id: str,
    body: RemoveAddQueueToWorker,
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    response: Response,
) -> None:
    """
    Adds an existing queue to a worker.

    Args:
        id (str): The id of the worker.
        body (RemoveAddQueueToWorker): The request body containing the queue name to add.
        auth (Auth): The user's authentication status.

    Raises:
        HTTPException: If the worker or queue cannot be found or if an error occurs during queue addition.
    """
    async with httpx.AsyncClient() as client:
        api_response = await client.post(
            f"{config.WORKER_URL}/worker/addQueue/{id}",
            headers={"Authorization": f"Bearer {config.WORKER_KEY}"},
            json=body.dict(),
        )

    response.status_code = api_response.status_code
    response.headers["x-queue-name-header"] = api_response.headers["x-queue-name-header"]

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Either the worker or the queue name does not exist")
    elif response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@router.post("/worker/removeQueue/{id}")
async def remove_queue(
    id: str,
    body: RemoveAddQueueToWorker,
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    response: Response,
) -> None:
    """
    Removes an existing queue from a worker.

    Args:
        id (str): The id of the worker.
        body (RemoveAddQueueToWorker): The request body containing the queue name to remove.
        auth (Auth): The user's authentication status.


    Raises:
        HTTPException: If the worker or queue cannot be found or if an error occurs during queue removal.
    """
    async with httpx.AsyncClient() as client:
        api_response = await client.post(
            f"{config.WORKER_URL}/worker/removeQueue/{id}",
            headers={"Authorization": f"Bearer {config.WORKER_KEY}"},
            json=body.dict(),
        )

    response.status_code = api_response.status_code
    response.headers["x-queue-name-header"] = api_response.headers["x-queue-name-header"]

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Either the worker or the queue name does not exist")
    elif response.status_code == 405:
        raise HTTPException(status_code=405, detail="A worker needs to have at least one queue")
    elif response.status_code == 406:
        raise HTTPException(status_code=406, detail="Queue after removal is not in use")
    elif response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@router.get("/worker/all")
async def get_workers(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
) -> list[GetWorkerWorkers]:
    """
    Get a list of all workers.

    Args:
        auth (Auth): The user's authentication status.

    Returns:
        list[GetWorkerWorkers]: A list of GetWorkerWorkers objects with status, queues,
        and job counts of a single worker.

    Raises:
        HTTPException: If an error occurs while retrieving the worker list.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{config.WORKER_URL}/worker/list_workers",
            headers={"Authorization": f"Bearer {config.WORKER_KEY}"},
            timeout=100,
        )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")

    return response.json()


@router.get("/worker/jobqueue/{id}")
async def get_jobqueue(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))], id: str
) -> list[GetWorkerJobqueue]:
    """
    Get a list of all job queues for the worker specified by the id.

    Args:
        id (str): The id of the worker.
        auth (Auth): The user's authentication status.

    Returns:
        list[GetWorkerJobqueue]: A list of job queue objects for the worker.

    Raises:
        HTTPException: If an error occurs while retrieving the job queues or the worker id is invalid.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{config.WORKER_URL}/worker/jobqueue/{id}",
            headers={"Authorization": f"Bearer {config.WORKER_KEY}"},
            timeout=100,
        )

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="No worker exists with this name")
    elif response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")

    return response.json()


@router.get("/worker/jobs/{id}")
async def get_jobs(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))], id: str
) -> list[GetWorkerJobs]:
    """
    Get a list of all jobs for the worker specified by the id.

    Args:
        id (str): The id of the worker.
        auth (Auth): The user's authentication status.

    Returns:
        list[GetWorkerJobs]: A list of jobs for the worker.

    Raises:
        HTTPException: If an error occurs while retrieving the jobs for the worker or the id is invalid.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{config.WORKER_URL}/worker/jobs/{id}",
            headers={"Authorization": f"Bearer {config.WORKER_KEY}"},
            timeout=100,
        )

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="No worker exists with this name")
    elif response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")

    return response.json()


@router.get("/worker/returningJobs/")
async def get_returningJobs(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
) -> list[GetWorkerReturningJobs]:
    """
    Get a list of all returning jobs of this worker / of the queues this worker consumes.

    Args:
        auth (Auth): The user's authentication status

    Returns:
        list[GetWorkerReturningJobs]: A list of returning jobs for the worker.

    Raises:
        HTTPException: If an error occurs while retrieving returning jobs for the worker or the id is invalid.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{config.WORKER_URL}/worker/returningJobs/",
            headers={"Authorization": f"Bearer {config.WORKER_KEY}"},
            timeout=100,
        )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")

    return response.json()
