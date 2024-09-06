from time import time

import pytest
import pytest_asyncio
from icecream import ic
from sqlalchemy.future import select

from mmisp.db.models.server import Server
from mmisp.tests.generators.model_generators.server_generator import generate_server


@pytest_asyncio.fixture
async def server(db, instance_owner_org):
    server = generate_server()
    server.org_id = instance_owner_org.id

    db.add(server)
    await db.commit()
    await db.refresh(server)

    yield server
    await db.delete(server)
    await db.commit()


@pytest.mark.asyncio
async def test_get_server(site_admin_user_token, instance_owner_org, server, client) -> None:
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


@pytest.mark.asyncio
async def test_get_servers(site_admin_user_token, instance_owner_org, server, client) -> None:
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


@pytest.mark.asyncio
async def test_add_remote_server(site_admin_user_token, client, db) -> None:
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

    await db.commit()
    query = select(Server).where(Server.id == json_str.get("id"))
    server = (await db.execute(query)).scalars().first()

    assert name == server.name
    assert server is not None

    await db.delete(server)
    await db.commit()


@pytest.mark.asyncio
async def test_delete_remote_server(site_admin_user_token, client, db) -> None:
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

    await db.commit()
    query = select(Server).where(Server.id == json_str.get("id"))
    server = (await db.execute(query)).scalars().first()

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
    await db.commit()
    server_deleted = (await db.execute(query)).scalars().first()
    assert server_deleted is None


@pytest_asyncio.fixture
async def generated_server(db, instance_owner_org):
    server = generate_server()
    server.org_id = instance_owner_org.id

    db.add(server)
    await db.commit()
    await db.refresh(server)

    yield server
    await db.delete(server)
    await db.commit()


@pytest.mark.asyncio
async def test_delete_remote_server_generated(site_admin_user_token, client, db, generated_server) -> None:
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
    await db.commit()
    server_deleted = (await db.execute(query)).scalars().first()
    assert server_deleted is None


@pytest.mark.asyncio
async def test_unauthorized_access(client, server) -> None:
    response = client.get(f"/servers/remote/{server.id}")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_invalid_server_id(site_admin_user_token, client) -> None:
    invalid_id = 99999
    response = client.get(f"/servers/remote/{invalid_id}", headers={"authorization": site_admin_user_token})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_server_with_missing_fields(site_admin_user_token, client) -> None:
    response = client.post(
        "/servers/remote/add",
        headers={"authorization": site_admin_user_token},
        json={
            "name": "missing_fields_server",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_edit_server(db, site_admin_user_token, client, instance_two_server) -> None:
    request = {
        "name": "server",
        "url": "test.url",
        "priority": 1,
        "authkey": "abc",
        "remote_org_id": 10,
        "internal": False,
        "push": True,
        "pull": True,
        "pull_rules": "rule1",
        "push_rules": "rule2",
        "push_galaxy_clusters": True,
        "caching_enabled": True,
        "unpublish_event": False,
        "publish_without_email": True,
        "self_signed": False,
        "skip_proxy": True,
    }
    edit_response = client.post(
        f"/servers/remote/edit/{instance_two_server.org_id}",
        headers={"authorization": site_admin_user_token},
        json=request,
    )

    edit_response_json = edit_response.json()
    assert isinstance(edit_response_json, list)
    assert edit_response_json[len(edit_response_json) - 1] is not None
    serv = edit_response_json[len(edit_response_json) - 1]
    assert serv["id"] == instance_two_server.id
    assert serv["name"] == request["name"]
    assert serv["url"] == request["url"]
    assert serv["authkey"] == request["authkey"]
    assert serv["org_id"] == instance_two_server.org_id
    assert serv["push"] == request["push"]
    assert serv["pull"] == request["pull"]
    assert serv["push_sightings"] == instance_two_server.push_sightings
    assert serv["push_galaxy_clusters"] == request["push_galaxy_clusters"]
    assert serv["pull_galaxy_clusters"] == instance_two_server.pull_galaxy_clusters
    assert serv["remote_org_id"] == request["remote_org_id"]
    assert serv["publish_without_email"] == request["publish_without_email"]
    assert serv["unpublish_event"] == request["unpublish_event"]
    assert serv["self_signed"] == request["self_signed"]
    assert serv["internal"] == request["internal"]
    assert serv["skip_proxy"] == request["skip_proxy"]
    assert serv["caching_enabled"] == request["caching_enabled"]
    assert serv["priority"] == request["priority"]
