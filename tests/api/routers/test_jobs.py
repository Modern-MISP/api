import pytest
import respx
from httpx import Response

from mmisp.api.config import config


@respx.mock
@pytest.mark.asyncio
async def test_get_job(site_admin_user_token, client) -> None:
    route = respx.get(f"{config.WORKER_URL}/job/1/result").mock(return_value=Response(200, json={}))

    response = client.get("/jobs/1", headers={"authorization": site_admin_user_token})

    assert response.status_code == 200
    json = response.json()
    assert json == {}
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_get_job_unfinished(site_admin_user_token, client) -> None:
    route = respx.get(f"{config.WORKER_URL}/job/1/result").mock(return_value=Response(409, json={}))

    response = client.get("/jobs/1", headers={"authorization": site_admin_user_token})

    assert response.status_code == 409
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_get_job_no_result(site_admin_user_token, client) -> None:
    route = respx.get(f"{config.WORKER_URL}/job/1/result").mock(return_value=Response(204, json={}))

    response = client.get("/jobs/1", headers={"authorization": site_admin_user_token})

    assert response.status_code == 204
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_get_job_unexpected_error(site_admin_user_token, client) -> None:
    route = respx.get(f"{config.WORKER_URL}/job/1/result").mock(return_value=Response(500, json={}))

    response = client.get("/jobs/1", headers={"authorization": site_admin_user_token})

    assert response.status_code == 500
    assert route.called
