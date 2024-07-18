from time import time

import pytest
import sqlalchemy as sa
from icecream import ic

from tests.generators.model_generators.auth_key_generator import generate_auth_key


def delete_auth_key(db, auth_key_id):
    stmt = sa.sql.text("DELETE FROM auth_keys WHERE id=:id")
    db.execute(stmt, {"id": auth_key_id})
    db.commit()


@pytest.fixture
def auth_key(db, instance_owner_org_admin_user):
    auth_key = generate_auth_key()
    auth_key.user_id = instance_owner_org_admin_user.id

    db.add(auth_key)
    db.commit()
    db.refresh(auth_key)
    yield auth_key

    db.delete(auth_key)
    db.commit()


def test_add_auth_key(db, site_admin_user_token, site_admin_user, client) -> None:
    body = {"comment": f"test key {time()}"}

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/auth_keys/{site_admin_user.id}", json=body, headers=headers)

    assert response.status_code == 201
    response_json = response.json()
    ic(response_json)

    assert response_json["AuthKey"]["comment"] == body["comment"]

    delete_auth_key(db, response_json["AuthKey"]["id"])


def test_add_auth_key_depr(db, site_admin_user_token, site_admin_user, client) -> None:
    body = {"comment": f"test key {time()}"}

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/auth_keys/add/{site_admin_user.id}", json=body, headers=headers)

    assert response.status_code == 201
    response_json = response.json()

    assert response_json["AuthKey"]["comment"] == body["comment"]
    delete_auth_key(db, response_json["AuthKey"]["id"])


def test_search_existing_auth_key_details(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/auth_keys", json={}, headers=headers)

    assert response.status_code == 200


def test_search_non_existing_auth_key_details(site_admin_user_token, client) -> None:
    body = {"id": "-1"}

    headers = {"authorization": site_admin_user_token}
    response = client.post("/auth_keys", json=body, headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert len(json) == 0


def test_get_existing_auth_key_details(auth_key, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/auth_keys/view/{auth_key.id}", headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert json["AuthKey"]["id"] == str(auth_key.id)


def test_get_non_existing_auth_key_details(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/auth_keys/view/-1", headers=headers)

    assert response.status_code == 404


def test_edit_auth_key(auth_key, instance_owner_org_admin_user_token, client) -> None:
    body = {"comment": f"updated {time()}"}

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.put(f"/auth_keys/{auth_key.id}", headers=headers, json=body)

    assert response.status_code == 200
    json = response.json()

    assert json["AuthKey"]["id"] == str(auth_key.id)
    assert json["AuthKey"]["comment"] == body["comment"]


def test_edit_auth_key_depr(auth_key, instance_owner_org_admin_user_token, client) -> None:
    body = {"comment": f"updated {time()}"}

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.post(f"/auth_keys/edit/{auth_key.id}", headers=headers, json=body)

    assert response.status_code == 200
    json = response.json()

    assert json["AuthKey"]["id"] == str(auth_key.id)
    assert json["AuthKey"]["comment"] == body["comment"]


def test_get_all_auth_keys(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/auth_keys", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_auth_key(auth_key, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/auth_keys/{auth_key.id}", headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert json["saved"]
    assert json["success"]
    assert "delete" not in json["url"]
    assert json["id"] == str(auth_key.id)


def test_delete_auth_key_depr(auth_key, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/auth_keys/delete/{auth_key.id}", headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert json["saved"]
    assert json["success"]
    assert "delete" in json["url"]
    assert json["id"] == str(auth_key.id)


def test_view_own_auth_keys(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/auth_keys/viewOwn", headers=headers)

    ic(response.json())

    assert response.status_code == 200
    response_json = response.json()
    ic(response_json)
    assert isinstance(response_json, list)
    for auth_key in response_json:
        assert isinstance(auth_key, list)


def test_view_own_auth_keys_depr(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/auth_keys/index/{userId}", headers=headers)

    ic(response.json())

    assert response.status_code == 200
    response_json = response.json()
    ic(response_json)
    assert isinstance(response_json, list)
    for auth_key in response_json:
        assert isinstance(auth_key, list)
