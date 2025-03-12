import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_get_all_attributes(
    access_test_objects,
    client,
) -> None:

    path = "/attributes"
    request_body = {}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}

@pytest.mark.asyncio
async def test_get_existing_attribute(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_get_existing_attribute_fail_read_only_user(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_get_existing_attribute_read_only_user_own_org(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["attribute_event_read_only_user"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_get_existing_attribute_fail_read_only_user_own_org(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["attribute_event_read_only_user_2"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}

