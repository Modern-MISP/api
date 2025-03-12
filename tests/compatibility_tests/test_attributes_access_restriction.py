import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_get_all_attributes(
    auth_key,
    access_test_objects,
    client,
) -> None:

    path = "/attributes"
    request_body = {}
   # clear_key = access_test_objects["default_read_only_user_clear_key"]
   # auth_key = access_test_objects["default_read_only_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}

