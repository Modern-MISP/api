from typing import Any, Dict

import pytest

from ...environment import client, environment
from ...generators.attribute_generator import (
    generate_existing_attribute_id,
    generate_invalid_attribute_id,
    generate_invalid_field_add_attribute_data,
    generate_invalid_required_field_add_attribute_data,
    generate_missing_required_field_add_attribute_data,
    generate_non_existing_attribute_id,
    generate_valid_add_attribute_data,
    generate_valid_edit_attribute_data,
)

# --- Test cases ---


# --- Test add attribute


@pytest.fixture(scope="module")
def add_attribute_valid_data() -> Dict[str, Any]:
    return generate_valid_add_attribute_data.dict()


def test_add_attribute_valid_data(add_attribute_valid_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/attributes/", json=add_attribute_valid_data, headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    for key, value in add_attribute_valid_data.items():
        response_json[key] == value


@pytest.mark.parametrize(
    "add_attribute_invalid_data",
    [
        generate_invalid_field_add_attribute_data.dict(),
        generate_invalid_required_field_add_attribute_data.dict(),
        generate_missing_required_field_add_attribute_data.dict(),
    ],
)
def test_add_attribute_missing_required_field(add_attribute_invalid_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/attributes/", json=add_attribute_invalid_data, headers=headers)
    assert response.status_code == 403


def test_add_attribute_response_format(add_attribute_valid_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/attributes/", json=add_attribute_valid_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"


def test_add_attribute_authorization(add_attribute_valid_data: Dict[str, Any]) -> None:
    headers = {"authorization": ""}
    response = client.post("/attributes/", json=add_attribute_valid_data, headers=headers)
    assert response.status_code == 401


# --- Test get attribute by id


@pytest.fixture(scope="module")
def existing_attribute_id() -> str:
    return generate_existing_attribute_id()


def test_get_existing_attribute(existing_attribute_id: str) -> None:
    response = client.get("/attributes/" + existing_attribute_id)
    assert response.status_code == 200
    assert response.json()["id"] == existing_attribute_id


@pytest.mark.parametrize(
    "invalid_or_non_existing_attribute_ids",
    [generate_non_existing_attribute_id, generate_invalid_attribute_id],
    scope="module",
)
def test_get_invalid_or_non_existing_attribute(invalid_or_non_existing_attribute_ids: str) -> None:
    response = client.get("/attributes/" + invalid_or_non_existing_attribute_ids)
    assert response.status_code == 404


def test_get_attribute_response_format(existing_attribute_id: str) -> None:
    response = client.get("/attributes/" + existing_attribute_id)
    assert response.headers["Content-Type"] == "application/json"


# --- Test edit attribute


@pytest.fixture()
def edit_attribute_valid_data() -> Dict[str, Any]:
    return generate_valid_edit_attribute_data().dict()


def test_edit_existing_attribute(existing_attribute_id: str, edit_attribute_valid_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.put("/attributes/" + existing_attribute_id, json=edit_attribute_valid_data, headers=headers)
    assert response.status_code == 200


def test_edit_non_existing_attribute(
    invalid_or_non_existing_attribute_ids: str, edit_attribute_valid_data: Dict[str, Any]
) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.put(
        "/attributes/" + invalid_or_non_existing_attribute_ids, json=edit_attribute_valid_data, headers=headers
    )
    assert response.status_code == 404


def test_edit_attribute_response_format(existing_attribute_id: str, edit_attribute_valid_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.put("/attributes/" + existing_attribute_id, json=edit_attribute_valid_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"


def test_edit_attribute_authorization(existing_attribute_id: str, edit_attribute_valid_data: Dict[str, Any]) -> None:
    headers = {"authorization": ""}
    response = client.put("/attributes/" + existing_attribute_id, json=edit_attribute_valid_data, headers=headers)
    assert response.status_code == 401


# --- Test delete attribute by id


def test_delete_existing_attribute(existing_attribute_id: str) -> None:
    response = client.delete("/attributes/" + existing_attribute_id)
    assert response.status_code == 200


def test_delete_invalid_or_non_existing_attribute(invalid_or_non_existing_attribute_ids: str) -> None:
    response = client.delete("/attributes/" + invalid_or_non_existing_attribute_ids)
    assert response.status_code == 404


def test_delete_attribute_response_format(existing_attribute_id: str) -> None:
    response = client.delete("/attributes/" + existing_attribute_id)
    assert response.headers["Content-Type"] == "application/json"
