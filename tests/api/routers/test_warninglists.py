from time import time

from sqlalchemy.orm import Session

from mmisp.api_schemas.warninglists.check_value_warninglists_body import CheckValueWarninglistsBody
from mmisp.api_schemas.warninglists.create_warninglist_body import (
    CreateWarninglistBody,
    WarninglistCategory,
    WarninglistListType,
)
from mmisp.api_schemas.warninglists.toggle_enable_warninglists_body import ToggleEnableWarninglistsBody
from mmisp.db.database import get_db
from mmisp.db.models.warninglist import Warninglist, WarninglistEntry
from tests.api.helpers.warninglist_helper import (
    add_warninglists,
    generate_enable_warning_lists_body,
    get_largest_id,
    remove_warninglists,
)
from tests.environment import client, environment


class TestAddWarninglist:
    @staticmethod
    def test_add_warninglists() -> None:
        data = CreateWarninglistBody(
            name=f"test warninglist{time()}",
            type=WarninglistListType.CIDR.value,
            description="test description",
            enabled=False,
            default=False,
            category=WarninglistCategory.KNOWN_IDENTIFIER.value,
            valid_attributes=["md5"],
            values="a b c",
        ).dict()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/warninglists/new", json=data, headers=headers)

        assert response.status_code == 201


class TestToggleEnableWarninglist:
    @staticmethod
    def test_toggleEnable_warninglist() -> None:
        warninglist_ids = add_warninglists()
        toggle_data = generate_enable_warning_lists_body(warninglist_ids).dict()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/warninglists/toggleEnable", json=toggle_data, headers=headers)

        assert response.status_code == 200

        remove_warninglists(warninglist_ids)

    @staticmethod
    def test_toggleEnable_missing_warninglist() -> None:
        invalid_toggle_data = ToggleEnableWarninglistsBody(
            id=["-1"],
            name="",
            enabled=False,
        ).dict()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/warninglists/toggleEnable", json=invalid_toggle_data, headers=headers)

        assert response.status_code == 200
        json = response.json()
        json["errors"] == "Warninglist(s) not found."


class TestGetWarninglistById:
    @staticmethod
    def test_get_existing_warninglist_details() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        warninglist_test_ids = add_warninglists()

        for warninglist_id in warninglist_test_ids:
            response = client.get(f"/warninglists/{warninglist_id}", headers=headers)

            assert response.status_code == 200
            assert response.json()["Warninglist"]["id"] == str(warninglist_id)

        remove_warninglists(warninglist_test_ids)

    @staticmethod
    def test_get_invalid_warninglist_by_id() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/warninglists/text", headers=headers)
        assert response.status_code == 422

    @staticmethod
    def test_get_non_existing_warninglist_details() -> None:
        non_existing_warninglist_id = get_largest_id() * 10

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/warninglists/{non_existing_warninglist_id}", headers=headers)
        assert response.status_code == 404

    @staticmethod
    def test_get_warninglist_response_format() -> None:
        warninglist_id = add_warninglists(1)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/warninglists/{warninglist_id[0]}", headers=headers)

        assert response.status_code == 200
        json = response.json()

        assert json["Warninglist"]["id"] == str(warninglist_id[0])
        assert isinstance(json["Warninglist"]["WarninglistEntry"], list)

        remove_warninglists(warninglist_id)


class TestDeleteWarninglist:
    @staticmethod
    def test_delete_existing_warninglist() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        warninglist_test_ids = add_warninglists()

        for warninglist_test_id in warninglist_test_ids:
            response = client.delete(f"/warninglists/{warninglist_test_id}", headers=headers)
            assert response.status_code == 200

    @staticmethod
    def test_delete_invalid_warninglist_by_id() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete("/warninglists/text", headers=headers)
        assert response.status_code == 422

    @staticmethod
    def test_delete_non_existing_warninglist() -> None:
        non_existing_warninglist_id = get_largest_id() * 10

        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/warninglists/{non_existing_warninglist_id}", headers=headers)
        assert response.status_code == 404

    @staticmethod
    def test_delete_warninglist_response_format() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        warninglist_test_ids = add_warninglists()

        for warninglist_id in warninglist_test_ids:
            response = client.delete(f"/warninglists/{warninglist_id}", headers=headers)

            assert response.status_code == 200
            json = response.json()

            assert isinstance(json["Warninglist"]["WarninglistEntry"], list)
            assert json["Warninglist"]["id"] == str(warninglist_id)


class TestGetAllOrSelectedWarninglists:
    @staticmethod
    def test_get_all_warninglist() -> None:
        headers = {"authorization": environment.site_admin_user_token}

        response = client.get("/warninglists", headers=headers)

        assert response.status_code == 200

    @staticmethod
    def test_get_all_warninglists() -> None:
        db: Session = get_db()
        warninglist_id = add_warninglists(1)

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

        remove_warninglists(warninglist_id)

    @staticmethod
    def test_get_all_warninglist_response_format() -> None:
        db: Session = get_db()
        warninglist_ids = add_warninglists(1)

        warninglist_name = db.get(Warninglist, warninglist_ids[0]).name

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/warninglists?value={warninglist_name}", headers=headers)
        json = response.json()
        assert isinstance(json["response"], list)

        remove_warninglists(warninglist_ids)


class TestGetWarninglistByValue:
    @staticmethod
    def test_get_warninglist_by_value() -> None:
        db: Session = get_db()
        warninglist_id = add_warninglists(1)

        warninglist_entry: WarninglistEntry = (
            db.query(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist_id[0]).first()
        )

        headers = {"authorization": environment.site_admin_user_token}
        value_data = CheckValueWarninglistsBody(value=[warninglist_entry.value]).dict()

        response = client.post("/warninglists/checkValue", json=value_data, headers=headers)

        assert response.status_code == 200
        json = response.json()

        assert next((entry for entry in json["response"] if entry["value"] == warninglist_entry.value), None)

        remove_warninglists(warninglist_id)

    @staticmethod
    def test_get_warninglist_by_value_response_format() -> None:
        db: Session = get_db()
        warninglist_ids = add_warninglists(1)

        warninglist_entry = (
            db.query(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist_ids[0]).first().value
        )

        headers = {"authorization": environment.site_admin_user_token}
        value_data = CheckValueWarninglistsBody(value=[warninglist_entry]).dict()

        response = client.post("/warninglists/checkValue", json=value_data, headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data["response"], list)

        remove_warninglists(warninglist_ids)


class TestUpdateWarninglist:
    @staticmethod
    def test_update_warninglist() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.put("/warninglists", headers=headers)
        assert response.status_code == 200

    @staticmethod
    def test_update_warninglist_response_format() -> None:
        headers = {"authorization": environment.site_admin_user_token}

        response = client.put("/warninglists", headers=headers)

        assert response.status_code == 200
        json = response.json()

        assert json["url"] == "/warninglists"

        response = client.post("/warninglists/update", headers=headers)

        assert response.status_code == 200
        json = response.json()

        assert json["url"] == "/warninglists/update"
