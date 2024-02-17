from typing import Any, Dict

import pytest
from sqlalchemy.orm import Session

from mmisp.api_schemas.warninglists.check_value_warninglists_body import CheckValueWarninglistsBody
from mmisp.db.database import get_db
from mmisp.db.models.warninglist import Warninglist, WarninglistEntry

from ...environment import client, environment
from ...generators.warninglist_generator import (
    add_warninglists,
    generate_invalid_togglelist,
    generate_random_invalid_warninglist_data,
    generate_random_valid_warninglist_data,
    generate_togglelist,
    get_largest_id,
    remove_warninglists,
)


@pytest.fixture(
    params=[
        generate_random_valid_warninglist_data().dict(),
        generate_random_valid_warninglist_data().dict(),
        generate_random_valid_warninglist_data().dict(),
        generate_random_valid_warninglist_data().dict(),
        generate_random_valid_warninglist_data().dict(),
    ]
)
def warninglist_data(request: Any) -> Dict[str, Any]:
    return request.param


@pytest.fixture(
    params=[
        generate_random_invalid_warninglist_data().dict(),
        generate_random_invalid_warninglist_data().dict(),
        generate_random_invalid_warninglist_data().dict(),
        generate_random_invalid_warninglist_data().dict(),
        generate_random_invalid_warninglist_data().dict(),
    ]
)
def invalid_warninglist_data(request: Any) -> Dict[str, Any]:
    return request.param


# --- Test cases ---


class TestAddWarninglist:
    def test_add_warninglists(self: "TestAddWarninglist", warninglist_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/warninglists/new", json=warninglist_data, headers=headers)

        assert response.status_code == 201

    def test_warninglist_error_handling(self: "TestAddWarninglist", invalid_warninglist_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/warninglists/new", json=invalid_warninglist_data, headers=headers)
        assert response.status_code == 422

    def test_warninglist_response_format(self: "TestAddWarninglist", warninglist_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/warninglists/new", json=warninglist_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"

    def test_add_warninglist_authorization(self: "TestAddWarninglist", warninglist_data: Dict[str, Any]) -> None:
        headers = {"authorization": ""}
        response = client.post("/warninglists/new", json=warninglist_data, headers=headers)
        assert response.status_code == 401


class TestToggleEnableWarninglist:
    def test_toggleEnable_warninglist(self: "TestToggleEnableWarninglist") -> None:
        warninglist_ids = add_warninglists()
        toggle_data = generate_togglelist(warninglist_ids).dict()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/warninglists/toggleEnable", json=toggle_data, headers=headers)

        assert response.status_code == 200

        remove_warninglists(warninglist_ids)

    def test_toggleEnable_missing_warninglist(self: "TestToggleEnableWarninglist") -> None:
        invalid_toggle_data = generate_invalid_togglelist().dict()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/warninglists/toggleEnable", json=invalid_toggle_data, headers=headers)

        assert response.status_code == 200
        json = response.json()
        json["errors"] == "Warninglist(s) not found."

    def test_warninglist_toggleEnable_response_format(self: "TestToggleEnableWarninglist") -> None:
        warninglist_ids = add_warninglists()
        toggle_data = generate_togglelist(warninglist_ids).dict()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("warninglists/toggleEnable", json=toggle_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"

        remove_warninglists(warninglist_ids)

    def test_toggleEnable_warninglist_authorization(self: "TestToggleEnableWarninglist") -> None:
        headers = {"authorization": ""}
        response = client.post("warninglists/toggleEnable/", json={}, headers=headers)
        assert response.status_code == 401


class TestGetWarninglistById:
    def test_get_existing_warninglist_details(self: "TestGetWarninglistById") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        warninglist_test_ids = add_warninglists()

        for warninglist_id in warninglist_test_ids:
            response = client.get(f"/warninglists/{warninglist_id}", headers=headers)

            assert response.status_code == 200
            assert response.json()["id"] == warninglist_id

        remove_warninglists(warninglist_test_ids)

    def test_get_invalid_warninglist_by_id(self: "TestGetWarninglistById") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        test = "text"
        response = client.get(f"/warninglists/{test}", headers=headers)
        assert response.status_code == 404

    def test_get_non_existing_warninglist_details(self: "TestGetWarninglistById") -> None:
        non_existing_warninglist_id = get_largest_id() * 10

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/warninglists/{non_existing_warninglist_id}", headers=headers)
        assert response.status_code == 404

    def test_get_warninglist_response_format(self: "TestGetWarninglistById") -> None:
        warninglist_id = add_warninglists(1)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/warninglists/{warninglist_id[0]}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == warninglist_id[0]
        assert isinstance(data["WarninglistEntry"], list)

        remove_warninglists(warninglist_id)


class TestDeleteWarninglist:
    def test_delete_existing_warninglist(self: "TestDeleteWarninglist") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        warninglist_test_ids = add_warninglists()

        for warninglist_test_id in warninglist_test_ids:
            response = client.delete(f"/warninglists/{warninglist_test_id}", headers=headers)
            assert response.status_code == 200

    def test_delete_invalid_warninglist_by_id(self: "TestDeleteWarninglist") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        test = "text"
        response = client.delete(f"/warninglists/{test}", headers=headers)
        assert response.status_code == 404

    def test_delete_non_existing_warninglist(self: "TestDeleteWarninglist") -> None:
        non_existing_warninglist_id = get_largest_id() * 10

        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/warninglists/{non_existing_warninglist_id}", headers=headers)
        assert response.status_code == 404

    def test_delete_warninglist_response_format(self: "TestDeleteWarninglist") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        warninglist_test_ids = add_warninglists()

        for warninglist_id in warninglist_test_ids:
            response = client.delete(f"/warninglists/{warninglist_id}", headers=headers)

            assert response.headers["Content-Type"] == "application/json"
            data = response.json()
            assert isinstance(data["WarninglistEntry"], list)
            assert data["id"] == warninglist_id


class TestGetAllOrSelectedWarninglists:
    def test_get_all_warninglist(self: "TestGetAllOrSelectedWarninglists") -> None:
        headers = {"authorization": environment.site_admin_user_token}

        response = client.get("/warninglists", headers=headers)

        assert response.status_code == 200

    def test_get_all_warninglists(self: "TestGetAllOrSelectedWarninglists") -> None:
        db: Session = get_db()
        warninglist_id, *_ = add_warninglists(1)
        warninglist: Warninglist = db.get(Warninglist, warninglist_id)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/warninglists?value={warninglist.name}&enabled=True", headers=headers)
        assert response.status_code == 200

        response = client.get(f"/warninglists?value={warninglist.name}", headers=headers)
        assert response.status_code == 200

        response = client.get("/warninglists?enabled=True", headers=headers)
        assert response.status_code == 200

        response = client.get("/warninglists?enabled=False", headers=headers)
        assert response.status_code == 200

        remove_warninglists([warninglist_id])

    def test_get_all_warninglist_response_format(self: "TestGetAllOrSelectedWarninglists") -> None:
        db: Session = get_db()
        warninglist_ids = add_warninglists(1)
        warninglist_name = db.get(Warninglist, warninglist_ids[0]).name

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/warninglists?value={warninglist_name}", headers=headers)
        json = response.json()
        assert isinstance(json["response"], list)

        remove_warninglists(warninglist_ids)


class TestGetWarninglistByValue:
    def test_get_warninglist_by_value(self: "TestGetWarninglistByValue") -> None:
        db: Session = get_db()
        warninglist_id, *_ = add_warninglists(1)
        warninglist_entry: WarninglistEntry = (
            db.query(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist_id).first()
        )

        headers = {"authorization": environment.site_admin_user_token}
        value_data = CheckValueWarninglistsBody(value=[warninglist_entry.value]).dict()
        response = client.post("/warninglists/checkValue", json=value_data, headers=headers)

        assert response.status_code == 200

        json = response.json()
        assert next((entry for entry in json["response"] if entry["value"] == warninglist_entry.value), None)

        remove_warninglists([warninglist_id])

    def test_get_warninglist_response_format(self: "TestGetWarninglistByValue") -> None:
        db: Session = get_db()
        warninglist_ids = add_warninglists(1)
        warninglist_entry = db.get(WarninglistEntry, warninglist_ids[0]).value

        headers = {"authorization": environment.site_admin_user_token}
        value_data = CheckValueWarninglistsBody(value=[warninglist_entry]).dict()
        response = client.post("/warninglists/checkValue", json=value_data, headers=headers)

        assert response.headers["Content-Type"] == "application/json"
        data = response.json()
        assert isinstance(data["response"], list)

        remove_warninglists(warninglist_ids)


class TestUpdateWarninglist:
    def test_update_warninglist(self: "TestUpdateWarninglist") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.put("/warninglists", headers=headers)
        assert response.status_code == 200

    def test_update_warninglist_response_format(self: "TestUpdateWarninglist") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.put("/warninglists", headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        jason = response.json()
        jason["url"] == "/warninglists"

        response = client.post("/warninglists/update", headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        jason = response.json()
        jason["url"] == "/warninglists/update"

    def test_update_warninglist_authorization(self: "TestUpdateWarninglist") -> None:
        headers = {"authorization": ""}
        response = client.put("/warninglists", headers=headers)
        assert response.status_code == 401
