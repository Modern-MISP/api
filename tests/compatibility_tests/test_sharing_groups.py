import pytest

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_get_single_sharing_group(
    db, sharing_group, auth_key, client, site_admin_user_token, instance_owner_org
) -> None:
    path = f"/sharing_groups/view/{sharing_group.id}"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_get_all_sharing_groups(
    db, sharing_group, auth_key, client, site_admin_user_token, instance_owner_org
) -> None:
    path = "/sharing_groups/index"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}
