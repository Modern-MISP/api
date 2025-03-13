import pytest
import respx
from httpx import Response

from mmisp.api.config import config


@respx.mock
@pytest.mark.asyncio
async def test_get_workers_success(site_admin_user_token, client) -> None:
    route = respx.get(f"{config.WORKER_URL}/worker/list_workers").mock(return_value=Response(200, json={}))

    response = client.get("/worker/all", headers={"authorization": site_admin_user_token})

    assert response.status_code == 200
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_get_workers_failure(site_admin_user_token, client) -> None:
    route = respx.get(f"{config.WORKER_URL}/worker/list_workers").mock(
        return_value=Response(404, json=[{"name": "nameabc", "status": "cba", "queues": ["halts Maus"], "jobCount": 7}])
    )

    response = client.get("/worker/all", headers={"authorization": site_admin_user_token})

    assert response.status_code == 500
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_get_jobs_workers_success(site_admin_user_token, client) -> None:
    route = respx.get(f"{config.WORKER_URL}/worker/jobs/abc").mock(
        return_value=Response(200, json=[{"placeInQueue": 1, "name": "cba", "queueName": "abc"}])
    )

    response = client.get("/worker/jobs/abc", headers={"authorization": site_admin_user_token})

    assert response.status_code == 200
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_get_jobs_workers_failure(site_admin_user_token, client) -> None:
    route = respx.get(f"{config.WORKER_URL}/worker/jobs/abc").mock(
        return_value=Response(404, json=[{"placeInQueue": 1, "name": "cba", "queueName": "abc"}])
    )

    response = client.get("/worker/jobs/abc", headers={"authorization": site_admin_user_token})

    assert response.status_code == 404
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_pause_worker_success(site_admin_user_token, client) -> None:
    resp = Response(200, json={})
    resp.headers["x-worker-name-header"] = "abc"
    route = respx.post(f"{config.WORKER_URL}/worker/pause/abc").mock(return_value=resp)

    response = client.post("/worker/pause/abc", headers={"authorization": site_admin_user_token})

    assert response.status_code == 200
    assert response.headers["x-worker-name-header"] == "abc"
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_pause_worker_failure(site_admin_user_token, client) -> None:
    resp = Response(404, json={})
    resp.headers["x-worker-name-header"] = "abc"
    route = respx.post(f"{config.WORKER_URL}/worker/pause/abc").mock(return_value=resp)

    response = client.post("/worker/pause/abc", headers={"authorization": site_admin_user_token})

    assert response.status_code == 404
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_unpause_worker_success(site_admin_user_token, client) -> None:
    resp = Response(200, json={})
    resp.headers["x-worker-name-header"] = "abc"
    route = respx.post(f"{config.WORKER_URL}/worker/unpause/abc").mock(return_value=resp)

    response = client.post("/worker/unpause/abc", headers={"authorization": site_admin_user_token})

    assert response.status_code == 200
    assert response.headers["x-worker-name-header"] == "abc"
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_unpause_worker_failure(site_admin_user_token, client) -> None:
    resp = Response(404, json={})
    resp.headers["x-worker-name-header"] = "abc"
    route = respx.post(f"{config.WORKER_URL}/worker/unpause/abc").mock(return_value=resp)

    response = client.post("/worker/unpause/abc", headers={"authorization": site_admin_user_token})

    assert response.status_code == 404
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_list_all_queues_worker_success(site_admin_user_token, client) -> None:
    route = respx.get(f"{config.WORKER_URL}/worker/jobqueue/abc").mock(
        return_value=Response(200, json=[{"name": "cba", "activ": "abc"}])
    )

    response = client.get("/worker/jobqueue/abc", headers={"authorization": site_admin_user_token})

    assert response.status_code == 200
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_list_all_queues_worker_failure(site_admin_user_token, client) -> None:
    route = respx.get(f"{config.WORKER_URL}/worker/jobqueue/abc").mock(
        return_value=Response(404, json=[{"name": "cba", "activ": "abc"}])
    )

    response = client.get("/worker/jobqueue/abc", headers={"authorization": site_admin_user_token})

    assert response.status_code == 404
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_returning_jobs_success(site_admin_user_token, client) -> None:
    route = respx.get(f"{config.WORKER_URL}/worker/returningJobs/").mock(
        return_value=Response(200, json=[{"name": "cba", "info": "abc", "nextExecution": "2018-06-12 09:55:22"}])
    )
    response = client.get("/worker/returningJobs/", headers={"authorization": site_admin_user_token})

    assert response.status_code == 200
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_returning_jobs_failure(site_admin_user_token, client) -> None:
    route = respx.get(f"{config.WORKER_URL}/worker/returningJobs/").mock(
        return_value=Response(404, json=[{"name": "cba", "info": "abc", "nextExecution": "2018-06-12 09:55:22"}])
    )

    response = client.get("/worker/returningJobs/", headers={"authorization": site_admin_user_token})

    assert response.status_code == 500
    assert route.called
