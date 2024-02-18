from time import time

from tests.database import get_db
from tests.environment import client, environment
from tests.generators.model_generators.auth_key_generator import generate_auth_key


class TestAddAuthKeys:
    @staticmethod
    def test_add_auth_key() -> None:
        body = {"comment": f"test key {time()}"}

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/auth_keys/{environment.site_admin_user.id}", json=body, headers=headers)

        assert response.status_code == 201
        response_json = response.json()

        assert response_json["AuthKey"]["comment"] == body["comment"]

    @staticmethod
    def test_add_auth_key_depr() -> None:
        body = {"comment": f"test key {time()}"}

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/auth_keys/add/{environment.site_admin_user.id}", json=body, headers=headers)

        assert response.status_code == 201
        response_json = response.json()

        assert response_json["AuthKey"]["comment"] == body["comment"]


class TestSearchAuthKeys:
    @staticmethod
    def test_search_existing_auth_key_details() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/auth_keys", json={}, headers=headers)

        assert response.status_code == 200

    @staticmethod
    def test_search_non_existing_auth_key_details() -> None:
        body = {"id": "-1"}

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/auth_keys", json=body, headers=headers)

        assert response.status_code == 200
        json = response.json()

        assert len(json) == 0


class TestViewAuthKey:
    @staticmethod
    def test_get_existing_auth_key_details() -> None:
        db = get_db()

        auth_key = generate_auth_key()
        auth_key.user_id = environment.instance_owner_org_admin_user.id

        db.add(auth_key)
        db.commit()
        db.refresh(auth_key)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/auth_keys/view/{auth_key.id}", headers=headers)

        assert response.status_code == 200
        json = response.json()

        assert json["AuthKey"]["id"] == str(auth_key.id)

    @staticmethod
    def test_get_non_existing_auth_key_details() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/auth_keys/view/-1", headers=headers)

        assert response.status_code == 404


class TestEditAuthKey:
    @staticmethod
    def test_edit_auth_key() -> None:
        db = get_db()

        auth_key = generate_auth_key()
        auth_key.user_id = environment.instance_owner_org_admin_user.id

        db.add(auth_key)
        db.commit()
        db.refresh(auth_key)

        body = {"comment": f"updated {time()}"}

        headers = {"authorization": environment.instance_owner_org_admin_user_token}
        response = client.put(f"/auth_keys/{auth_key.id}", headers=headers, json=body)

        assert response.status_code == 200
        json = response.json()

        assert json["AuthKey"]["id"] == str(auth_key.id)
        assert json["AuthKey"]["comment"] == body["comment"]

    @staticmethod
    def test_edit_auth_key_depr() -> None:
        db = get_db()

        auth_key = generate_auth_key()
        auth_key.user_id = environment.instance_owner_org_admin_user.id

        db.add(auth_key)
        db.commit()
        db.refresh(auth_key)

        body = {"comment": f"updated {time()}"}

        headers = {"authorization": environment.instance_owner_org_admin_user_token}
        response = client.post(f"/auth_keys/edit/{auth_key.id}", headers=headers, json=body)

        assert response.status_code == 200
        json = response.json()

        assert json["AuthKey"]["id"] == str(auth_key.id)
        assert json["AuthKey"]["comment"] == body["comment"]


class TestGetAuthKeys:
    @staticmethod
    def test_get_all_auth_keys() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/auth_keys", headers=headers)

        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestDeleteAuthKeys:
    @staticmethod
    def test_delete_auth_key() -> None:
        db = get_db()

        auth_key = generate_auth_key()
        auth_key.user_id = environment.instance_owner_org_admin_user.id

        db.add(auth_key)
        db.commit()
        db.refresh(auth_key)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/auth_keys/{auth_key.id}", headers=headers)

        assert response.status_code == 200
        json = response.json()

        assert json["saved"]
        assert json["success"]
        assert "delete" not in json["url"]
        assert json["id"] == str(auth_key.id)

    @staticmethod
    def test_delete_auth_key_depr() -> None:
        db = get_db()

        auth_key = generate_auth_key()
        auth_key.user_id = environment.instance_owner_org_admin_user.id

        db.add(auth_key)
        db.commit()
        db.refresh(auth_key)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/auth_keys/delete/{auth_key.id}", headers=headers)

        assert response.status_code == 200
        json = response.json()

        assert json["saved"]
        assert json["success"]
        assert "delete" in json["url"]
        assert json["id"] == str(auth_key.id)
