from ...environment import client, environment
from ...generators.noticelist_generator import (
    add_noticelists,
    get_invalid_noticelist_ids,
    get_non_existing_noticelist_ids,
    remove_noticelists,
)


class TestGetNoticelist:
    def test_get_existing_noticelist_details(self: "TestGetNoticelist") -> None:
        headers = {"authorization": environment.site_admin_user_token}

        noticelist_ids = add_noticelists()

        for noticelist_id in noticelist_ids:
            response = client.get(f"/noticelists/{noticelist_id}", headers=headers)
            assert response.status_code == 200
            assert response.json()["id"] == noticelist_id

        remove_noticelists(noticelist_ids)

    def test_get_invalid_noticelist_details(self: "TestGetNoticelist") -> None:
        headers = {"authorization": environment.site_admin_user_token}

        invalid_noticelist_ids = get_invalid_noticelist_ids()

        for invalid_noticelist_id in invalid_noticelist_ids:
            response = client.get(f"/noticelists/{invalid_noticelist_id}", headers=headers)
            assert response.status_code == 404

    def test_get_non_existing_noticelist_details(self: "TestGetNoticelist") -> None:
        headers = {"authorization": environment.site_admin_user_token}

        non_existing_noticelist_ids = get_non_existing_noticelist_ids()

        for non_existing_noticelist_id in non_existing_noticelist_ids:
            response = client.get(f"/noticelists/{non_existing_noticelist_id}", headers=headers)
            assert response.status_code == 404

    def test_get_noticelist_response_format(self: "TestGetNoticelist") -> None:
        headers = {"authorization": environment.site_admin_user_token}

        noticelist_id = add_noticelists(1)

        response = client.get(f"/noticelists/{noticelist_id[0]}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], int)

        remove_noticelists(noticelist_id)


class TestToggleEnableNoticelist:
    def test_toggleEnable_noticelist(self: "TestToggleEnableNoticelist") -> None:
        headers = {"authorization": environment.site_admin_user_token}

        noticelist_ids = add_noticelists()

        for noticelist_id in noticelist_ids:
            response = client.post(f"/noticelists/toggleEnable/{noticelist_id}", headers=headers)

            assert response.status_code == 200
            json = response.json()
            assert json["message"] == "Noticelist disabled."

            response = client.post(f"/noticelists/toggleEnable/{noticelist_id}", headers=headers)

            assert response.status_code == 200
            json = response.json()
            assert json["message"] == "Noticelist enabled."

            response = client.post(f"/noticelists/toggleEnable/{noticelist_id}", headers=headers)

            assert response.status_code == 200
            json = response.json()
            assert json["message"] == "Noticelist disabled."

    def test_toggleEnable_invalid_noticelist(self: "TestToggleEnableNoticelist") -> None:
        headers = {"authorization": environment.site_admin_user_token}

        invalid_noticelist_ids = get_invalid_noticelist_ids()

        for invalid_noticelist_id in invalid_noticelist_ids:
            response = client.post(f"/noticelists/toggleEnable/{invalid_noticelist_id}", headers=headers)
            assert response.status_code == 404

    def test_toggleEnable_non_existing_noticelist_details(self: "TestToggleEnableNoticelist") -> None:
        headers = {"authorization": environment.site_admin_user_token}

        non_existing_noticelist_ids = get_non_existing_noticelist_ids()

        for non_existing_noticelist_id in non_existing_noticelist_ids:
            response = client.post(f"/noticelists/toggleEnable/{non_existing_noticelist_id}", headers=headers)
            assert response.status_code == 404

    def test_noticelist_toggleEnable_response_format(self: "TestToggleEnableNoticelist") -> None:
        headers = {"authorization": environment.site_admin_user_token}

        noticelist_id = add_noticelists(1)

        response = client.post(f"noticelists/toggleEnable/{noticelist_id[0]}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"

        remove_noticelists(noticelist_id)

    def test_toggleEnable_noticelist_authorization(self: "TestToggleEnableNoticelist") -> None:
        headers = {"authorization": ""}
        response = client.post("noticelists/toggleEnable/{noticelist_ids['valid_noticelist_id']}", headers=headers)
        assert response.status_code == 401


class TestUpdateNoticelist:
    def test_update_noticelist(self: "TestUpdateNoticelist") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.put("/noticelists", headers=headers)
        assert response.status_code == 200

    def test_update_noticelist_response_format_new(self: "TestUpdateNoticelist") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.put("/noticelists", headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        data = response.json()
        assert data["url"] == "/noticelists/"

    def test_update_noticelist_response_format_old(self: "TestUpdateNoticelist") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/noticelists/update", headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        data = response.json()
        assert data["url"] == "/noticelists/update"

    def test_update_noticelist_authorization(self: "TestUpdateNoticelist") -> None:
        headers = {"authorization": ""}
        response = client.put("/noticelists", headers=headers)
        assert response.status_code == 401


# TODO: Add/double test for deprecated endpoints


class TestGetAllNoticelists:
    def test_get_all_noticelist(self: "TestGetAllNoticelists") -> None:
        headers = {"authorization": environment.site_admin_user_token}

        response = client.get("/noticelists", headers=headers)

        assert response.status_code == 200

    def test_get_noticelist_response_format(self: "TestGetAllNoticelists") -> None:
        headers = {"authorization": environment.site_admin_user_token}

        noticelist_ids = add_noticelists()

        response = client.get("/noticelists", headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], list)
        remove_noticelists(noticelist_ids)
