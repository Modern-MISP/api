from time import time

from sqlalchemy.orm import Session

from mmisp.api_schemas.warninglists.check_value_warninglists_body import CheckValueWarninglistsBody
from mmisp.api_schemas.warninglists.create_warninglist_body import (
    CreateWarninglistBody,
    WarninglistCategory,
    WarninglistListType,
)
from mmisp.api_schemas.warninglists.get_selected_warninglists_body import GetSelectedWarninglistsBody
from mmisp.api_schemas.warninglists.toggle_enable_warninglists_body import ToggleEnableWarninglistsBody
from mmisp.db.models.warninglist import Warninglist, WarninglistEntry
from tests.api.helpers.warninglists_helper import (
    add_warninglists,
    generate_enable_warning_lists_body,
    get_largest_id,
    remove_warninglists,
)


def test_add_warninglists(db, site_admin_user_token, client) -> None:
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

    headers = {"authorization": site_admin_user_token}
    response = client.post("/warninglists/new", json=data, headers=headers)

    assert response.status_code == 201

    json = response.json()
    remove_warninglists(db, [int(json["Warninglist"]["id"])])


def test_toggleEnable_warninglist(db, site_admin_user_token, client) -> None:
    warninglist_ids = add_warninglists(db)
    toggle_data = generate_enable_warning_lists_body(warninglist_ids).dict()

    headers = {"authorization": site_admin_user_token}
    response = client.post("/warninglists/toggleEnable", json=toggle_data, headers=headers)

    assert response.status_code == 200

    remove_warninglists(db, warninglist_ids)


def test_toggleEnable_missing_warninglist(db, site_admin_user_token, client) -> None:
    invalid_toggle_data = ToggleEnableWarninglistsBody(
        id=["-1"],
        name="",
        enabled=False,
    ).dict()

    headers = {"authorization": site_admin_user_token}
    response = client.post("/warninglists/toggleEnable", json=invalid_toggle_data, headers=headers)

    assert response.status_code == 200
    json = response.json()
    json["errors"] == "Warninglist(s) not found."

    warninglist_test_ids = add_warninglists(db)

    for warninglist_id in warninglist_test_ids:
        response = client.get(f"/warninglists/{warninglist_id}", headers=headers)

        assert response.status_code == 200
        assert response.json()["Warninglist"]["id"] == str(warninglist_id)

    remove_warninglists(db, warninglist_test_ids)


def test_get_existing_warninglist_details_deprecated(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    warninglist_test_ids = add_warninglists(db)

    for warninglist_id in warninglist_test_ids:
        response = client.get(f"/warninglists/view/{warninglist_id}", headers=headers)

        assert response.status_code == 200
        assert response.json()["Warninglist"]["id"] == str(warninglist_id)

    remove_warninglists(db, warninglist_test_ids)


def test_get_invalid_warninglist_by_id(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/warninglists/text", headers=headers)
    assert response.status_code == 422


def test_get_invalid_warninglist_by_id_deprecated(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/warninglists/view/text", headers=headers)
    assert response.status_code == 422


def test_get_non_existing_warninglist_details(db, site_admin_user_token, client) -> None:
    non_existing_warninglist_id = get_largest_id(db) * 10

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/warninglists/{non_existing_warninglist_id}", headers=headers)
    assert response.status_code == 404


def test_get_non_existing_warninglist_details_deprecated(db, site_admin_user_token, client) -> None:
    non_existing_warninglist_id = get_largest_id(db) * 10

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/warninglists/view/{non_existing_warninglist_id}", headers=headers)
    assert response.status_code == 404


def test_get_warninglist_response_format(db, site_admin_user_token, client) -> None:
    warninglist_id = add_warninglists(db, 1)

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/warninglists/{warninglist_id[0]}", headers=headers)

    assert response.status_code == 200
    json = response.json()

    print(json)
    assert json["Warninglist"]["id"] == str(warninglist_id[0])
    assert isinstance(json["Warninglist"]["WarninglistEntry"], list)

    remove_warninglists(db, warninglist_id)


def test_get_warninglist_response_format_deprecated(db, site_admin_user_token, client) -> None:
    warninglist_id = add_warninglists(db, 1)

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/warninglists/view/{warninglist_id[0]}", headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert json["Warninglist"]["id"] == str(warninglist_id[0])
    assert isinstance(json["Warninglist"]["WarninglistEntry"], list)

    remove_warninglists(db, warninglist_id)


def test_delete_existing_warninglist(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    warninglist_test_ids = add_warninglists(db)

    for warninglist_test_id in warninglist_test_ids:
        response = client.delete(f"/warninglists/{warninglist_test_id}", headers=headers)
        assert response.status_code == 200


def test_delete_invalid_warninglist_by_id(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete("/warninglists/text", headers=headers)
    assert response.status_code == 422


def test_delete_non_existing_warninglist(db, site_admin_user_token, client) -> None:
    non_existing_warninglist_id = get_largest_id(db) * 10

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/warninglists/{non_existing_warninglist_id}", headers=headers)
    assert response.status_code == 404


def test_delete_warninglist_response_format(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    warninglist_test_ids = add_warninglists(db)

    for warninglist_id in warninglist_test_ids:
        response = client.delete(f"/warninglists/{warninglist_id}", headers=headers)

        assert response.status_code == 200
        json = response.json()

        assert isinstance(json["Warninglist"]["WarninglistEntry"], list)
        assert json["Warninglist"]["id"] == str(warninglist_id)


def test_get_all_warninglist(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    response = client.get("/warninglists", headers=headers)

    assert response.status_code == 200


def test_get_selected_warninglists(db: Session, site_admin_user_token, client) -> None:
    warninglist_id = add_warninglists(db, 1)

    warninglist: Warninglist = db.get(Warninglist, warninglist_id)

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/warninglists?value={warninglist.name}&enabled=True", headers=headers)
    assert response.status_code == 200

    response = client.get(f"/warninglists?value={warninglist.name}", headers=headers)
    assert response.status_code == 200

    response = client.get("/warninglists?enabled=True", headers=headers)
    assert response.status_code == 200

    response = client.get("/warninglists?enabled=False", headers=headers)
    assert response.status_code == 200

    remove_warninglists(db, warninglist_id)


def test_get_selected_warninglists_deprecated(db: Session, site_admin_user_token, client) -> None:
    warninglist_id = add_warninglists(db, 1)

    warninglist: Warninglist = db.get(Warninglist, warninglist_id)

    data = GetSelectedWarninglistsBody(value=warninglist.name, enabled=warninglist.enabled).dict()
    headers = {"authorization": site_admin_user_token}
    response = client.post("/warninglists", json=data, headers=headers)
    assert response.status_code == 200

    data = GetSelectedWarninglistsBody(value=warninglist.name).dict()
    response = client.post("/warninglists", json=data, headers=headers)
    assert response.status_code == 200

    data = GetSelectedWarninglistsBody(enabled=warninglist.enabled).dict()
    response = client.post("/warninglists", json=data, headers=headers)
    assert response.status_code == 200

    data = GetSelectedWarninglistsBody().dict()
    response = client.post("/warninglists", json=data, headers=headers)
    assert response.status_code == 200

    remove_warninglists(db, warninglist_id)


def test_get_all_warninglist_response_format(db: Session, site_admin_user_token, client) -> None:
    warninglist_ids = add_warninglists(db, 1)

    warninglist_name = db.get(Warninglist, warninglist_ids[0]).name

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/warninglists?value={warninglist_name}", headers=headers)
    json = response.json()
    assert isinstance(json["Warninglists"], list)

    remove_warninglists(db, warninglist_ids)


def test_get_warninglist_by_value(db: Session, site_admin_user_token, client) -> None:
    warninglist_id = add_warninglists(db, 1)

    warninglist_entry: WarninglistEntry = (
        db.query(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist_id[0]).first()
    )

    headers = {"authorization": site_admin_user_token}
    value_data = CheckValueWarninglistsBody(value=warninglist_entry.value).dict()

    response = client.post("/warninglists/checkValue", json=value_data, headers=headers)

    assert response.status_code == 200

    remove_warninglists(db, warninglist_id)


def test_get_warninglist_by_value_response_format(db: Session, site_admin_user_token, client) -> None:
    warninglist_ids = add_warninglists(db, 1)

    warninglist_entry: WarninglistEntry = (
        db.query(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist_ids[0]).first()
    )

    headers = {"authorization": site_admin_user_token}
    value = warninglist_entry.value
    value_data = CheckValueWarninglistsBody(value=value).dict()

    response = client.post("/warninglists/checkValue", json=value_data, headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert isinstance(json[f"{value}"], list)

    remove_warninglists(db, warninglist_ids)


def test_update_warninglist(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.put("/warninglists", headers=headers)
    assert response.status_code == 200


def test_update_warninglist_deprecated(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/warninglists/update", headers=headers)
    assert response.status_code == 200


def test_update_warninglist_response_format(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    response = client.put("/warninglists", headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert json["url"] == "/warninglists"


def test_update_warninglist_response_format_deprecated(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    response = client.post("/warninglists/update", headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert json["url"] == "/warninglists/update"
