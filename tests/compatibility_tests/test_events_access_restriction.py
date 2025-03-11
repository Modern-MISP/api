import pytest

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_list_all_events_self_created(access_test_objects, client) -> None:
    path = "/events"
    request_body = None
    assert get_legacy_modern_diff("get", path, request_body, access_test_objects["default_user_token"], client) == {}
