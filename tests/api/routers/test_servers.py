from time import time

import pytest
from icecream import ic
from sqlalchemy.future import select

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


def test_add_remote_server(site_admin_user_token, client, db) -> None:
    name = "test_user" + str(time())

    response = client.post(
        "/servers/remote/add",
        headers={"authorization": site_admin_user_token},
        json={
            "name": name,
            "url": "default_url",
            "priority": 1,
            "authkey": "default_authkey",
            "org_id": 2,
            "remote_org_id": 3,
            "internal": False,
            "push": False,
            "pull": False,
            "pull_rules": "default_pull_rules",
            "push_rules": "default_push_rules",
            "push_galaxy_clusters": False,
            "caching_enabled": False,
            "unpublish_event": False,
            "publish_without_email": False,
            "self_signed": False,
            "skip_proxy": False,
        },
    )

    # Check if the Status Code is 200
    json_str = response.json()
    assert response.status_code == 200

    db.commit()
    query = select(Server).where(Server.id == json_str.get("id"))
    server = db.execute(query).scalars().first()

    assert name == server.name
    assert server is not None

    db.delete(server)
    db.commit()


def test_delete_remote_server(site_admin_user_token, client, db) -> None:
    name = "test_user" + str(time())

    response = client.post(
        "/servers/remote/add",
        headers={"authorization": site_admin_user_token},
        json={
            "name": name,
            "url": "default_url",
            "priority": 1,
            "authkey": "default_authkey",
            "org_id": 2,
            "remote_org_id": 3,
            "internal": False,
            "push": False,
            "pull": False,
            "pull_rules": "default_pull_rules",
            "push_rules": "default_push_rules",
            "push_galaxy_clusters": False,
            "caching_enabled": False,
            "unpublish_event": False,
            "publish_without_email": False,
            "self_signed": False,
            "skip_proxy": False,
        },
    )
    # Check if the Status Code is 200
    json_str = response.json()
    assert response.status_code == 200

    db.commit()
    query = select(Server).where(Server.id == json_str.get("id"))
    server = db.execute(query).scalars().first()

    assert name == server.name
    assert server is not None

    # delete api call
    server_id = server.id
    response_delete = client.delete(
        f"/servers/remote/delete/{server_id}",
        headers={"authorization": site_admin_user_token},
    )
    # check status
    assert response_delete.status_code == 200
    json_str_delete = response_delete.json()
    assert json_str_delete["success"] is True
    assert json_str_delete["message"] == "Remote server deleted successfully."

    # check delete
    db.commit()
    server_deleted = db.execute(query).scalars().first()
    assert server_deleted is None


@pytest.fixture
def generated_server(db, instance_owner_org) -> Server:
    server = generate_server()
    server.org_id = instance_owner_org.id

    db.add(server)
    db.commit()
    db.refresh(server)

    yield server
    db.delete(server)
    db.commit()


def test_delete_remote_server_generated(site_admin_user_token, client, db, generated_server) -> None:
    server = generated_server

    # Test if server was created
    assert server is not None

    # delete api call
    server_id = server.id
    response_delete = client.delete(
        f"/servers/remote/delete/{server_id}",
        headers={"authorization": site_admin_user_token},
    )

    # check status
    assert response_delete.status_code == 200
    json_str_delete = response_delete.json()
    assert json_str_delete["success"] is True
    assert json_str_delete["message"] == "Remote server deleted successfully."

    # check delete
    query = select(Server).where(Server.id == server_id)
    db.commit()
    server_deleted = db.execute(query).scalars().first()
    assert server_deleted is None


def test_unauthorized_access(client, server) -> None:
    response = client.get(f"/servers/remote/{server.id}")
    assert response.status_code == 403


def test_invalid_server_id(site_admin_user_token, client) -> None:
    invalid_id = 99999
    response = client.get(f"/servers/remote/{invalid_id}", headers={"authorization": site_admin_user_token})
    assert response.status_code == 404


def test_create_server_with_missing_fields(site_admin_user_token, client) -> None:
    response = client.post(
        "/servers/remote/add",
        headers={"authorization": site_admin_user_token},
        json={
            "name": "missing_fields_server",
        },
    )
    assert response.status_code == 422
