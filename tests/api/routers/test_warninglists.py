from typing import Any, Dict

import pytest

from mmisp.api_schemas.warninglists.check_value_warninglists_body import CheckValueWarninglistsBody

from ...environment import client, environment
from ...generators.warninglist_generator import (
    add_warninglists,
    generate_random_invalid_warninglist_data,
    generate_random_valid_warninglist_data,
    generate_togglelist,
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
# Test dummy
def test_dummy() -> None:
    print("hello")


# Test add a warninglist
def test_add_warninglists(warninglist_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/warninglists/new", json=warninglist_data, headers=headers)

    assert response.status_code == 201


def test_warninglist_data_integrity(warninglist_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/warninglists/new", json=warninglist_data, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        warninglist = response_json["warninglist"]
        for key in warninglist_data:
            assert warninglist[key] == warninglist_data[key], f"Fehlerhafte Datenintegrität für Feld {key}"


def test_warninglist_error_handling(invalid_warninglist_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/warninglists/new", json=invalid_warninglist_data, headers=headers)
    assert response.status_code == 422


# TODO: right format
def test_warninglist_response_format(warninglist_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/warninglists/new", json=warninglist_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"


def test_add_warninglist_authorization(warninglist_data: Dict[str, Any]) -> None:
    headers = {"authorization": ""}
    response = client.post("/warninglists/new", json=warninglist_data, headers=headers)
    assert response.status_code == 401


# Test toggleEnable warninglist
@pytest.fixture(
    params=[
        generate_togglelist().dict(),
    ]
)
def toggle_data(request: Any) -> Dict[str, Any]:
    return request.param


def test_toggleEnable_warninglist(toggle_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/warninglists/toggleEnable", json=toggle_data, headers=headers)

    assert response.status_code == 200


def test_warninglist_toggleEnable_response_format(toggle_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("warninglists/toggleEnable", json=toggle_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"


def test_toggleEnable_warninglist_authorization(toggle_data: Dict[str, Any]) -> None:
    headers = {"authorization": ""}
    response = client.post("warninglists/toggleEnable/", json=toggle_data, headers=headers)
    assert response.status_code == 401


# Test get warninglist by id
def test_get_existing_warninglist_details() -> None:
    headers = {"authorization": environment.site_admin_user_token}
    warninglist_test_ids = add_warninglists()

    for warninglist_id in warninglist_test_ids:
        response = client.get(f"/warninglists/{warninglist_id}", headers=headers)

        assert response.status_code == 200
        assert response.json()["id"] == warninglist_id

    # remove_warninglists(warninglist_test_ids)


def test_get_invalid_warninglist_by_id() -> None:
    headers = {"authorization": environment.site_admin_user_token}
    test = "text"
    response = client.get(f"/warninglists/{test}", headers=headers)
    assert response.status_code == 404


def test_get_non_existing_warninglist_details() -> None:
    headers = {"authorization": environment.site_admin_user_token}
    test = 1000
    response = client.get(f"/warninglists/{test}", headers=headers)
    assert response.status_code == 404


# TODO: right format
# def test_get_warninglist_response_format() -> None:
#     headers = {"authorization": environment.site_admin_user_token}
#     test = 228
#     response = client.get(f"/warninglists/{test}", headers=headers)
#     assert response.headers["Content-Type"] == "application/json"
#     data = response.json()
#     assert "warninglist" in data
#     assert isinstance(data["warninglist"], list)


# Test delete warninglist
def test_delete_existing_warninglist() -> None:
    headers = {"authorization": environment.site_admin_user_token}
    warninglist_test_ids = add_warninglists()

    for warninglist_test_id in warninglist_test_ids:
        response = client.delete(f"/warninglists/{warninglist_test_id}", headers=headers)
        assert response.status_code == 200


def test_delete_invalid_warninglist_by_id() -> None:
    headers = {"authorization": environment.site_admin_user_token}
    test = "text"
    response = client.get(f"/warninglists/{test}", headers=headers)
    assert response.status_code == 404


# TODO: magic number
def test_delete_non_existing_warninglist() -> None:
    headers = {"authorization": environment.site_admin_user_token}
    test = 1000
    response = client.get(f"/warninglists/{test}", headers=headers)
    assert response.status_code == 404


# TODO: right format
# def test_delete_warninglist_response_format() -> None:
#     headers = {"authorization": environment.site_admin_user_token}
#     warninglist_test_ids = add_warninglists()

#     for warninglist_id in warninglist_test_ids:
#         response = client.delete(f"/warninglists/{warninglist_id}", headers=headers)

#         assert response.headers["Content-Type"] == "application/json"
#         data = response.json()
#         assert "warninglist" in data
#         assert isinstance(data["warninglist"], list)


# Test get all warninglists or selected by value and enabled
def test_get_all_warninglist() -> None:
    headers = {"authorization": environment.site_admin_user_token}

    response = client.get("/warninglists", headers=headers)

    assert response.status_code == 200


# TODO: Magic String
def test_get_warninglist_by_value_false() -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.get("/warninglists?value=QiYt8ph0qO&enabled=False", headers=headers)
    assert response.status_code == 200


# TODO: Magic String
def test_get_warninglist_by_value_true() -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.get("/warninglists?value=QiYt8ph0qO&enabled=True", headers=headers)
    assert response.status_code == 200


# TODO: right format
# def test_get_warninglist_response_format() -> None:
#     headers = {"authorization": environment.site_admin_user_token}
#     response = client.get("/warninglists", headers=headers)
#     assert response.headers["Content-Type"] == "application/json"
#     data = response.json()
#     assert "warninglist" in data
#     assert isinstance(data["warninglist"], list)


# Test get warninglist by value
def test_get_warninglist_by_value() -> None:
    headers = {"authorization": environment.site_admin_user_token}
    # TODO: Magic string
    value_data = CheckValueWarninglistsBody(value=[]).dict()
    response = client.post("/warninglists/checkValue", json=value_data, headers=headers)

    assert response.status_code == 200


# TODO: right format
# def test_get_warninglist_response_format() -> None:
#     headers = {"authorization": environment.site_admin_user_token}
#     # TODO: Magic string
#     value_data = CheckValueWarninglistsBody(value=["KSQDMIk4m5", "yTKhI3V5ec"]).dict()
#     response = client.post("/warninglists/checkValue", json=value_data, headers=headers)

#     assert response.headers["Content-Type"] == "application/json"
#     data = response.json()
#     assert "warninglist" in data
#     assert isinstance(data["warninglist"], list)


# Test update warninglist
def test_update_warninglist() -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.put("/warninglists", headers=headers)
    assert response.status_code == 200


# TODO: format
# def test_update_warninglist_response_format() -> None:
#     headers = {"authorization": environment.site_admin_user_token}
#     response = client.put("/warninglists", headers=headers)
#     assert response.headers["Content-Type"] == "application/json"
#     assert "warninglist" in response.json()


def test_update_warninglist_authorization() -> None:
    headers = {"authorization": ""}
    response = client.put("/warninglists", headers=headers)
    assert response.status_code == 401


# TODO: Add/double test for deprecated endpoints
