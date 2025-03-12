import pytest

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_list_all_events_self_created(access_test_objects, client) -> None:
    path = "/events"
    request_body = None
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}

@pytest.mark.asyncio
async def test_list_all_events_admin(access_test_objects, auth_key, client) -> None:
    headers = {"authorization": access_test_objects["site_admin_user_token"]}
    response = client.get("/events", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}

