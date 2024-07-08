import pytest
from icecream import ic

from mmisp.db.models.server import Server
from tests.generators.model_generators.server_generator import generate_server


@pytest.fixture
def server(db, instance_owner_org) -> Server:
    server = generate_server()
    server.org_id = instance_owner_org.id

    db.add(server)
    db.commit()
    db.refresh(server)

    yield server
    db.delete(server)
    db.commit()


def test_get_server(site_admin_user_token, instance_owner_org, server, client) -> None:
    result = client.get(f"/servers/remote/{server.id}", headers={"authorization": site_admin_user_token})

    assert result.status_code == 200
    response = result.json()
    assert response["id"] == server.id
    assert response["org_id"] == instance_owner_org.id
    assert response["name"] == server.name
    assert response["url"] == server.url
    assert response["authkey"] == server.authkey
    assert response["push"] == server.push
    assert response["pull"] == server.pull
    assert response["push_sightings"] == server.push_sightings
    assert response["push_galaxy_clusters"] == server.push_galaxy_clusters
    assert response["pull_galaxy_clusters"] == server.pull_galaxy_clusters
    assert response["remote_org_id"] == server.remote_org_id
    assert response["publish_without_email"] == server.publish_without_email
    assert response["unpublish_event"] == server.unpublish_event
    assert response["self_signed"] == server.self_signed
    assert response["internal"] == server.internal
    assert response["skip_proxy"] == server.skip_proxy
    assert response["caching_enabled"] == server.caching_enabled
    assert response["priority"] == server.priority


def test_get_servers(site_admin_user_token, instance_owner_org, server, client) -> None:
    result = client.get("/servers/remote/getAll", headers={"authorization": site_admin_user_token})

    assert result.status_code == 200
    response = result.json()
    ic(response)
    assert isinstance(response, list)
    assert response[len(response) - 1] is not None
    serv = response[len(response) - 1]
    assert serv["id"] == server.id
    assert serv["org_id"] == instance_owner_org.id
    assert serv["name"] == server.name
    assert serv["url"] == server.url
    assert serv["authkey"] == server.authkey
    assert serv["push"] == server.push
    assert serv["pull"] == server.pull
    assert serv["push_sightings"] == server.push_sightings
    assert serv["push_galaxy_clusters"] == server.push_galaxy_clusters
    assert serv["pull_galaxy_clusters"] == server.pull_galaxy_clusters
    assert serv["remote_org_id"] == server.remote_org_id
    assert serv["publish_without_email"] == server.publish_without_email
    assert serv["unpublish_event"] == server.unpublish_event
    assert serv["self_signed"] == server.self_signed
    assert serv["internal"] == server.internal
    assert serv["skip_proxy"] == server.skip_proxy
    assert serv["caching_enabled"] == server.caching_enabled
    assert serv["priority"] == server.priority
