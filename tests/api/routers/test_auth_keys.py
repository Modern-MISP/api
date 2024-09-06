from datetime import datetime
from time import time

import pytest
import pytest_asyncio
import sqlalchemy as sa
from icecream import ic

from mmisp.api.auth import encode_token
from mmisp.api.routers.auth_keys import parse_date
from mmisp.tests.generators.model_generators.auth_key_generator import generate_auth_key


async def delete_auth_key(db, auth_key_id):
    stmt = sa.sql.text("DELETE FROM auth_keys WHERE id=:id")
    await db.execute(stmt, {"id": auth_key_id})
    await db.commit()


@pytest_asyncio.fixture
async def read_only_user_token(view_only_user):
    return encode_token(view_only_user.id)


@pytest_asyncio.fixture
async def auth_key(db, instance_owner_org_admin_user):
    auth_key = generate_auth_key()
    auth_key.user_id = instance_owner_org_admin_user.id

    db.add(auth_key)
    await db.commit()
    await db.refresh(auth_key)
    yield auth_key

    await db.delete(auth_key)
    await db.commit()


@pytest.mark.asyncio
async def test_add_auth_key(db, site_admin_user_token, site_admin_user, client) -> None:
    body = {"comment": f"test key {time()}"}

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/auth_keys/{site_admin_user.id}", json=body, headers=headers)

    assert response.status_code == 201
    response_json = response.json()
    ic(response_json)

    assert response_json["AuthKey"]["comment"] == body["comment"]

    await delete_auth_key(db, response_json["AuthKey"]["id"])


@pytest.mark.asyncio
async def test_add_auth_key_depr(db, site_admin_user_token, site_admin_user, client) -> None:
    body = {"comment": f"test key {time()}"}

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/auth_keys/add/{site_admin_user.id}", json=body, headers=headers)

    assert response.status_code == 201
    response_json = response.json()

    assert response_json["AuthKey"]["comment"] == body["comment"]
    await delete_auth_key(db, response_json["AuthKey"]["id"])


@pytest.mark.asyncio
async def test_search_existing_auth_key_details(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/auth_keys", json={}, headers=headers)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_non_existing_auth_key_details(site_admin_user_token, client) -> None:
    body = {"id": "-1"}

    headers = {"authorization": site_admin_user_token}
    response = client.post("/auth_keys", json=body, headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert len(json) == 0


@pytest.mark.asyncio
async def test_get_existing_auth_key_details(auth_key, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/auth_keys/view/{auth_key.id}", headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert json["AuthKey"]["id"] == str(auth_key.id)


@pytest.mark.asyncio
async def test_get_non_existing_auth_key_details(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/auth_keys/view/-1", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_edit_auth_key(auth_key, instance_owner_org_admin_user_token, client) -> None:
    body = {"comment": f"updated {time()}"}

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.put(f"/auth_keys/{auth_key.id}", headers=headers, json=body)

    assert response.status_code == 200
    json = response.json()

    assert json["AuthKey"]["id"] == str(auth_key.id)
    assert json["AuthKey"]["comment"] == body["comment"]


@pytest.mark.asyncio
async def test_edit_auth_key_depr(auth_key, instance_owner_org_admin_user_token, client) -> None:
    body = {"comment": f"updated {time()}"}

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.post(f"/auth_keys/edit/{auth_key.id}", headers=headers, json=body)

    assert response.status_code == 200
    json = response.json()

    assert json["AuthKey"]["id"] == str(auth_key.id)
    assert json["AuthKey"]["comment"] == body["comment"]


@pytest.mark.asyncio
async def test_get_all_auth_keys(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/auth_keys", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_view_own_auth_keys(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/auth_keys/viewOwn", headers=headers)

    ic(response.json())

    assert response.status_code == 200
    response_json = response.json()
    ic(response_json)
    assert isinstance(response_json, list)
    for auth_key in response_json:
        assert isinstance(auth_key, list)


@pytest.mark.asyncio
async def test_view_own_auth_keys_depr(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/auth_keys/index/{userId}", headers=headers)

    ic(response.json())

    assert response.status_code == 200
    response_json = response.json()
    ic(response_json)
    assert isinstance(response_json, list)
    for auth_key in response_json:
        assert isinstance(auth_key, list)


@pytest.mark.asyncio
async def test_get_all_auth_keys_with_params(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/auth_keys?limit=10&page=2", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_view_auth_key_details_unauthorized(auth_key, client) -> None:
    response = client.get(f"/auth_keys/view/{auth_key.id}")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_auth_key_invalid_uuid(db, site_admin_user_token, site_admin_user, client) -> None:
    body = {"uuid": "invalid-uuid", "comment": f"test key {time()}"}

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/auth_keys/{site_admin_user.id}", json=body, headers=headers)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_edit_auth_key_invalid_id(instance_owner_org_admin_user_token, client) -> None:
    body = {"comment": f"updated {time()}"}

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.put("/auth_keys/invalid-id", headers=headers, json=body)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_non_existing_auth_key(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete("/auth_keys/-1", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_view_own_auth_keys_no_auth(client) -> None:
    response = client.get("/auth_keys/viewOwn")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_search_auth_keys_invalid_input(client, site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    body = {"limit": 1000}  # Invalid limit > 500
    response = client.post("/auth_keys", json=body, headers=headers)
    assert response.status_code == 422  # Unprocessable Entity

    body = {"page": 0}  # Invalid page < 1
    response = client.post("/auth_keys", json=body, headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_view_own_auth_keys_deprecated_route(client, instance_owner_org_admin_user_token) -> None:
    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.get("/auth_keys/index/{userId}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_keys_delete_not_found(client, site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete("/auth_keys/0", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_auth_keys_view_own(client, instance_owner_org_admin_user_token) -> None:
    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.get("/auth_keys/viewOwn", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_auth_keys_view_unauthorized_user(auth_key, client, read_only_user_token) -> None:
    ic(read_only_user_token)
    ic(auth_key)
    headers = {"authorization": read_only_user_token}
    response = client.get(f"/auth_keys/view/{auth_key.id}", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_auth_keys_edit_unauthorized_user(auth_key, client, read_only_user_token) -> None:
    body = {"comment": f"updated {time()}"}
    headers = {"authorization": read_only_user_token}
    response = client.put(f"/auth_keys/{auth_key.id}", json=body, headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_auth_key(auth_key, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/auth_keys/{auth_key.id}", headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert json["saved"]
    assert json["success"]
    assert "delete" not in json["url"]
    assert json["id"] == str(auth_key.id)


@pytest.mark.asyncio
async def test_delete_auth_key_depr(auth_key, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/auth_keys/delete/{auth_key.id}", headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert json["saved"]
    assert json["success"]
    assert "delete" in json["url"]
    assert json["id"] == str(auth_key.id)


@pytest.mark.asyncio
async def test_parse_date_valid():
    assert parse_date("2024-08-02") == int(datetime(2024, 8, 2).timestamp())


@pytest.mark.asyncio
async def test_parse_date_invalid_format():
    with pytest.raises(ValueError, match="Date must be in the format yyyy-mm-dd"):
        parse_date("02/08/2024")


@pytest.mark.asyncio
async def test_parse_date_invalid_date():
    with pytest.raises(ValueError, match="Invalid date format"):
        parse_date("2024-02-30")
