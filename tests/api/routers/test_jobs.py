import respx
from httpx import Response

from mmisp.config import config

from ...environment import client, environment


@respx.mock
def test_get_job() -> None:
    route = respx.get(f"{config.WORKER_URL}/jobs/1/status").mock(return_value=Response(200, json={}))

    response = client.get("/jobs/1", headers={"authorization": environment.site_admin_user_token})

    assert response.status_code == 200
    json = response.json()
    assert json == {}
    assert route.called