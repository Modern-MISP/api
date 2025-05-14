import pytest
from sqlalchemy import delete

from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement
from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_get_galaxy_cluster(
    db, test_galaxy, auth_key, client, site_admin_user_token, instance_owner_org, server
) -> None:
    galaxy_cluster = test_galaxy["galaxy_cluster"]
    path = f"/galaxy_clusters/view/{galaxy_cluster.id}"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_get_default_galaxy_cluster(
    db, test_default_galaxy, auth_key, client, site_admin_user_token, instance_owner_org, server
) -> None:
    galaxy_cluster = test_default_galaxy["galaxy_cluster"]
    path = f"/galaxy_clusters/view/{galaxy_cluster.id}"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_add_galaxy_cluster(
    db, test_galaxy, auth_key, client, site_admin_user_token, instance_owner_org, server
) -> None:
    def preprocessor(modern, legacy):
        del modern["GalaxyCluster"]["id"]
        del legacy["GalaxyCluster"]["id"]
        del modern["GalaxyCluster"]["tag_name"]
        del legacy["GalaxyCluster"]["tag_name"]
        del modern["GalaxyCluster"]["uuid"]
        del legacy["GalaxyCluster"]["uuid"]
        for ge in legacy["GalaxyCluster"]["GalaxyElement"]:
            del ge["galaxy_cluster_id"]
            del ge["id"]
        for ge in modern["GalaxyCluster"]["GalaxyElement"]:
            del ge["galaxy_cluster_id"]
            del ge["id"]
        assert (int(modern["GalaxyCluster"]["version"]) - int(legacy["GalaxyCluster"]["version"])) < 100
        del modern["GalaxyCluster"]["version"]
        del legacy["GalaxyCluster"]["version"]

    galaxy = test_galaxy["galaxy"]
    path = f"/galaxy_clusters/add/{galaxy.id}"
    request_body = {
        "value": "test add",
        "description": "test add",
        "source": "test add",
        "authors": ["test author 1", "test author 2"],
        "distribution": 3,
        "GalaxyElement": [{"key": "test key", "value": "test value"}],
    }
    assert get_legacy_modern_diff("post", path, request_body, auth_key, client, preprocessor=preprocessor) == {}

    await db.execute(delete(GalaxyElement).filter(GalaxyElement.value == "test value"))
    await db.execute(delete(GalaxyCluster).filter(GalaxyCluster.value == "test add"))
    await db.commit()


@pytest.mark.asyncio
async def test_get_all_galaxy_cluster(
    db, auth_key, client, test_galaxy, site_admin_user_token, instance_owner_org, server
) -> None:
    galaxy = test_galaxy["galaxy"]
    path = f"/galaxy_clusters/index/{galaxy.id}"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}
