import pytest

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_get_galaxy_cluster(
    db, test_galaxy, auth_key, client, site_admin_user_token, instance_owner_org, server
) -> None:
    galaxy_cluster = test_galaxy["galaxy_cluster"]
    path = f"/galaxy_clusters/view/{galaxy_cluster.id}"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}
