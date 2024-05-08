import respx
from httpx import Response

from mmisp.api.config import config

from ...environment import client


@respx.mock
def test_get_job(site_admin_user_token) -> None:
    route = respx.get(f"{config.WORKER_URL}/jobs/1/status").mock(return_value=Response(200, json={}))

    response = client.get("/jobs/1", headers={"authorization": site_admin_user_token})

    assert response.status_code == 200
    json = response.json()
    assert json == {}
    assert route.called
