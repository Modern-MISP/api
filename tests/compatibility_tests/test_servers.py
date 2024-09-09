from time import time

import pytest
import pytest_asyncio

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff
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
async def test_get_server(db, auth_key, client, site_admin_user_token, instance_owner_org, server) -> None:
    path = "/servers"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_add_remote_server_minimal(site_admin_user_token, auth_key, client, db) -> None:
    path = "/servers/add"
    request_body = {
        "name": f"test_server{str(time())}",
        "url": "http://misp.example.com",
        "authkey": "Vee0ohl0ahQuoop0tahdeiphaichaghooc0oof2a",
        "remote_org_id": 1,
    }

    def preprocessor(modern, legacy):
        del modern["Server"]["id"]
        del legacy["Server"]["id"]
        del modern["Server"]["priority"]
        del legacy["Server"]["priority"]

    assert get_legacy_modern_diff("post", path, request_body, auth_key, client, preprocessor=preprocessor) == {}
