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
async def test_list_all_events_admin(auth_key, client) -> None:
    path = "/events"
    request_body = None
    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}

