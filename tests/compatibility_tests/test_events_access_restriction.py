import pytest

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff

"""
@pytest.mark.asyncio
async def test_list_all_events_self_created(access_test_objects, client) -> None:
    path = "/events"
    request_body = {"distribution": 0}
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}




@pytest.mark.asyncio
async def test_list_all_events_read_only_user(access_test_objects, client) -> None:

@pytest.mark.asyncio
async def test_list_all_events_admin(auth_key, client) -> None:
    path = "/events"
    request_body = {"distribution": 0}
    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}
"""


@pytest.mark.asyncio
async def test_get_event_success_read_only_user(access_test_objects, client) -> None:
    path = "/events/" + str(access_test_objects["event_read_only_user"].id)
    request_body = {"distribution": 0}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}

@pytest.mark.asyncio
async def test_get_event_fail_read_only_user(access_test_objects, client) -> None:
    path = "/events/" + str(access_test_objects["default_event"].id)
    request_body = {"distribution": 0}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}
