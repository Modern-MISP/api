from typing import Any, Dict

import pytest

from ...environment import client, environment
from ...generators.attribute_generator import (
    generate_existing_id,
    generate_invalid_field_add_attribute_data,
    generate_invalid_id,
    generate_invalid_required_field_add_attribute_data,
    generate_invalid_search_attributes_data,
    generate_missing_required_field_add_attribute_data,
    generate_missing_required_field_search_attribute_data,
    generate_non_existing_id,
    generate_valid_add_attribute_data,
    generate_valid_delete_selected_attributes_data,
    generate_valid_edit_attribute_data,
    generate_valid_search_attributes_data,
)

# --- Test cases ---


# --- Test add attribute


@pytest.fixture(scope="module")
def add_attribute_valid_data() -> Dict[str, Any]:
    return generate_valid_add_attribute_data().dict()


def test_add_attribute_valid_data(add_attribute_valid_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/attributes/", json=add_attribute_valid_data, headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    for key, value in add_attribute_valid_data.items():
        assert response_json[key] == value


@pytest.fixture(
    params=[
        generate_invalid_field_add_attribute_data().dict(),
        generate_invalid_required_field_add_attribute_data().dict(),
        generate_missing_required_field_add_attribute_data().dict(),
    ],
    scope="module",
)
def add_attribute_invalid_data(request: Any) -> Dict[str, Any]:
    return request.param


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
def existing_id() -> str:
    return generate_existing_id()


def test_get_existing_attribute(existing_id: str) -> None:
    response = client.get("/attributes/" + existing_id)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json[0] == "Attribute"
    attribute = response_json[0]
    assert attribute["id"] == existing_id
    for field in attribute:
        assert "id" in field
        assert "event_id" in field
        assert "object_id" in field
        assert "object_relation" in field
        assert "category" in field
        assert "type" in field
        assert "value" in field
        assert "to_ids" in field
        assert "uuid" in field
        assert "timestamp" in field
        assert "distribution" in field
        assert "sharing_group_id" in field
        assert "comment" in field
        assert "deleted" in field
        assert "disable_correlation" in field
        assert "first_seen" in field
        assert "last_seen" in field
        assert "Tag" in field


@pytest.fixture(params=[generate_non_existing_id, generate_invalid_id], scope="module")
def invalid_or_non_existing_ids(request: Any) -> str:
    request.param


def test_get_invalid_or_non_existing_attribute(invalid_or_non_existing_ids: str) -> None:
    response = client.get("/attributes/" + invalid_or_non_existing_ids)
    assert response.status_code == 404


def test_get_attribute_response_format(existing_id: str) -> None:
    response = client.get("/attributes/" + existing_id)
    assert response.headers["Content-Type"] == "application/json"


# --- Test edit attribute


@pytest.fixture()
def edit_attribute_valid_data() -> Dict[str, Any]:
    return generate_valid_edit_attribute_data().dict()


def test_edit_existing_attribute(existing_id: str, edit_attribute_valid_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.put("/attributes/" + existing_id, json=edit_attribute_valid_data, headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json[0] == "Attribute"
    attribute = response_json["Attribute"][0]
    assert attribute["id"] == existing_id
    for key, value in edit_attribute_valid_data.items():
        assert attribute[key] == value


def test_edit_non_existing_attribute(
    invalid_or_non_existing_ids: str, edit_attribute_valid_data: Dict[str, Any]
) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.put("/attributes/" + invalid_or_non_existing_ids, json=edit_attribute_valid_data, headers=headers)
    assert response.status_code == 404


def test_edit_attribute_response_format(existing_id: str, edit_attribute_valid_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.put("/attributes/" + existing_id, json=edit_attribute_valid_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"


def test_edit_attribute_authorization(existing_id: str, edit_attribute_valid_data: Dict[str, Any]) -> None:
    headers = {"authorization": ""}
    response = client.put("/attributes/" + existing_id, json=edit_attribute_valid_data, headers=headers)
    assert response.status_code == 401


# --- Test delete attribute by id


def test_delete_existing_attribute(existing_id: str) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.delete("/attributes/" + existing_id, headers=headers)
    assert response.status_code == 200


def test_delete_invalid_or_non_existing_attribute(invalid_or_non_existing_ids: str) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.delete("/attributes/" + invalid_or_non_existing_ids, headers=headers)
    assert response.status_code == 404


def test_delete_attribute_response_format(existing_id: str) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.delete("/attributes/" + existing_id, headers=headers)
    assert response.headers["Content-Type"] == "application/json"


def test_delete_attribute_authorization(existing_id: str) -> None:
    headers = {"authorization": ""}
    response = client.delete("/attributes/" + existing_id, headers=headers)
    assert response.status_code == 401


# --- Test get all attributes


def test_get_all_attributes() -> None:
    response = client.get("/attributes/")
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    for attribute in response_json:
        assert "id" in attribute
        assert "event_id" in attribute
        assert "object_id" in attribute
        assert "object_relation" in attribute
        assert "category" in attribute
        assert "type" in attribute
        assert "value" in attribute
        assert "value1" in attribute
        assert "value2" in attribute
        assert "to_ids" in attribute
        assert "uuid" in attribute
        assert "timestamp" in attribute
        assert "distribution" in attribute
        assert "sharing_group_id" in attribute
        assert "comment" in attribute
        assert "deleted" in attribute
        assert "disable_correlation" in attribute
        assert "first_seen" in attribute
        assert "last_seen" in attribute


def test_get_all_attributes_response_format() -> None:
    response = client.get("/attributes/")
    assert response.headers["Content-Type"] == "application/json"


# --- Test delete selected attribute(s)


@pytest.fixture()
def delete_selected_attributes_data() -> Dict[str, Any]:
    return generate_valid_delete_selected_attributes_data().dict()


def test_delete_selected_attributes_from_existing_event(
    existing_id: str, delete_selected_existing_attributes_data: Dict[str, Any]
) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(
        "/attributes/deleteSelected/" + existing_id, json=delete_selected_existing_attributes_data, headers=headers
    )
    assert response.status_code == 200
    response_json = response.json()
    counter_of_selected_attributes = delete_selected_attributes_data["id"].count(" ") + 1
    if counter_of_selected_attributes == 1:
        assert response_json["message"] == str(counter_of_selected_attributes) + "attribute deleted"
    else:
        assert response_json["message"] == str(counter_of_selected_attributes) + "attributes deleted"


def test_delete_selected_attributes_response_format(
    existing_id: str, delete_selected_existing_attributes_data: Dict[str, Any]
) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(
        "/attributes/deleteSelected/" + existing_id, json=delete_selected_existing_attributes_data, headers=headers
    )
    assert response.headers["Content-Type"] == "application/json"


def test_delete_selected_attributes_authorization(
    existing_id: str, delete_selected_existing_attributes_data: Dict[str, Any]
) -> None:
    headers = {"authorization": ""}
    response = client.post(
        "/attributes/deleteSelected/" + existing_id, json=delete_selected_existing_attributes_data, headers=headers
    )
    assert response.status_code == 401


@pytest.fixture(scope="module")
def search_attribute_valid_data() -> Dict[str, Any]:
    return generate_valid_search_attributes_data().dict()


def test_valid_search_attribute_data(search_attribute_valid_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/attributes/restSearch", json=search_attribute_valid_data, headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json[0] == "response"
    response_json_attribute = response_json["response"][0]
    assert response_json_attribute == "Attribute"
    response_json_details = response_json_attribute["Attribute"][0]
    for key, value in search_attribute_valid_data:
        assert response_json_details[key] == value


@pytest.fixture(
    params=[
        generate_invalid_search_attributes_data().dict(),
        generate_missing_required_field_search_attribute_data().dict(),
    ]
)
def search_attributes_invalid_data(request: Any) -> Dict[str, Any]:
    return request.param


def test_invalid_or_missing_required_field_search_attribute_data(
    search_attributes_invalid_data: Dict[str, Any],
) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/attributes/restSearch", json=search_attributes_invalid_data, headers=headers)
    assert response.status_code == 404


def test_search_attributes_response_format(search_attribute_valid_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/attributes/restSearch", json=search_attribute_valid_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"


def test_search_attributes_authorization(search_attribute_valid_data: Dict[str, Any]) -> None:
    headers = {"authorization": ""}
    response = client.post("/attributes/restSearch", json=search_attribute_valid_data, headers=headers)
    assert response.status_code == 401
