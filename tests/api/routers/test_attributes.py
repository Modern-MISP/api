from random import Random
from typing import Any, Dict

import pytest
from sqlalchemy.orm import Session

from mmisp.api_schemas.attributes.get_describe_types_response import GetDescribeTypesAttributes
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.event import Event
from mmisp.db.models.tag import Tag

from ...environment import client, environment, get_db
from ...generators.attribute_generator import (
    generate_existing_id,
    generate_invalid_context_and_percentage_attribute_statistics,
    generate_invalid_field_add_attribute_data,
    generate_invalid_id,
    generate_invalid_required_field_add_attribute_data,
    generate_invalid_search_attributes_data,
    generate_non_existing_id,
    generate_valid_add_attribute_data,
    generate_valid_context_and_percentage_attribute_statistics,
    generate_valid_delete_selected_attributes_data,
    generate_valid_edit_attribute_data,
    generate_valid_local_add_tag_to_attribute,
    generate_valid_search_attributes_data,
)


@pytest.fixture(scope="function")
def db() -> Session:
    db_session = get_db()

    yield db_session

    db_session.close()


@pytest.fixture(scope="module")
def add_attribute_valid_data() -> Dict[str, Any]:
    return generate_valid_add_attribute_data().dict()


@pytest.fixture(params=[generate_non_existing_id, generate_invalid_id], scope="module")
def invalid_or_non_existing_ids(request: Any) -> Any:
    request.param


@pytest.fixture(
    params=[
        generate_invalid_field_add_attribute_data().dict(),
        generate_invalid_required_field_add_attribute_data().dict(),
    ],
    scope="module",
)
def add_attribute_invalid_data(request: Any) -> Dict[str, Any]:
    return request.param


@pytest.fixture()
def edit_attribute_valid_data() -> Dict[str, Any]:
    return generate_valid_edit_attribute_data().dict()


@pytest.fixture(scope="module")
def delete_selected_existing_attributes_data() -> Dict[str, Any]:
    return generate_valid_delete_selected_attributes_data().dict()


@pytest.fixture(scope="module")
def search_attribute_valid_data() -> Dict[str, Any]:
    return generate_valid_search_attributes_data().dict()


@pytest.fixture(scope="module")
def existing_id() -> str:
    return generate_existing_id()


@pytest.fixture(scope="module")
def search_attributes_invalid_data() -> Dict[str, Any]:
    return generate_invalid_search_attributes_data().dict()


@pytest.fixture(scope="module")
def valid_parameters_attribute_statistics() -> Dict[str, Any]:
    return generate_valid_context_and_percentage_attribute_statistics()


@pytest.fixture(scope="module")
def invalid_parameters_attribute_statistics() -> Dict[str, Any]:
    return generate_invalid_context_and_percentage_attribute_statistics()


@pytest.fixture(scope="module")
def valid_local_add_tag_to_attribute() -> int:
    return generate_valid_local_add_tag_to_attribute()


# --- Test cases ---


# --- Test add attribute


class TestAddAttribute:
    def test_add_attribute_valid_data(
        self: "TestAddAttribute", db: Session, add_attribute_valid_data: Dict[str, Any]
    ) -> None:
        add_event_body = Event(info="test")

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = str(add_event_body.id)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/attributes/{event_id}", json=add_attribute_valid_data, headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["Attribute"]["value"] == add_attribute_valid_data["value"]
        assert response_json["Attribute"]["type"] == add_attribute_valid_data["type"]
        assert response_json["Attribute"]["category"] == add_attribute_valid_data["category"]
        assert response_json["Attribute"]["to_ids"] == add_attribute_valid_data["to_ids"]
        assert response_json["Attribute"]["distribution"] == add_attribute_valid_data["distribution"]
        assert response_json["Attribute"]["comment"] == add_attribute_valid_data["comment"]
        assert response_json["Attribute"]["disable_correlation"] == add_attribute_valid_data["disable_correlation"]

    def test_add_attribute_invalid_event_id(
        self: "TestAddAttribute", invalid_or_non_existing_ids: str, add_attribute_valid_data: Dict[str, Any]
    ) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            f"/attributes/{invalid_or_non_existing_ids}",
            json=add_attribute_valid_data,
            headers=headers,
        )
        assert response.status_code == 404

    def test_add_attribute_invalid_data(
        self: "TestAddAttribute", existing_id: str, add_attribute_invalid_data: Dict[str, Any]
    ) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/attributes/{existing_id}", json=add_attribute_invalid_data, headers=headers)
        assert response.status_code == 403

    def test_add_attribute_response_format(
        self: "TestAddAttribute", existing_id: str, add_attribute_valid_data: Dict[str, Any]
    ) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/attributes/{existing_id}", json=add_attribute_valid_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"

    def test_add_attribute_authorization(
        self: "TestAddAttribute", existing_id: str, add_attribute_valid_data: Dict[str, Any]
    ) -> None:
        headers = {"authorization": ""}
        response = client.post(f"/attributes/{existing_id}", json=add_attribute_valid_data, headers=headers)
        assert response.status_code == 401


# --- Test get attribute by id


class TestGetAttributeDetails:
    def test_get_existing_attribute(self: "TestGetAttributeDetails", db: Session) -> None:
        add_event_body = Event(info="test")

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = str(add_event_body.id)

        add_attribute_body = Attribute(value="test", value1="test", type="text", category="Other", event_id=event_id)

        db.add(add_attribute_body)
        db.commit()
        db.refresh(add_attribute_body)

        attribute_id = add_attribute_body.id

        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(0, 100000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            is_galaxy=False,
            is_custom_galaxy=False,
            attribute_count=1,
            count=1,
            favourite=False,
            local_only=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_id = add_tag_body.id

        add_attribute_tag_body = AttributeTag(attribute_id=attribute_id, event_id=event_id, tag_id=tag_id, local=False)

        db.add(add_attribute_tag_body)
        db.commit()
        db.refresh(add_attribute_tag_body)

        response = client.get(f"/attributes/{attribute_id}")

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["Attribute"]["id"] == str(attribute_id)
        assert response_json["Attribute"]["event_id"] == str(event_id)
        assert "id" in response_json["Attribute"]
        assert "event_id" in response_json["Attribute"]
        assert "object_id" in response_json["Attribute"]
        assert "object_relation" in response_json["Attribute"]
        assert "category" in response_json["Attribute"]
        assert "type" in response_json["Attribute"]
        assert "value" in response_json["Attribute"]
        assert "to_ids" in response_json["Attribute"]
        assert "uuid" in response_json["Attribute"]
        assert "timestamp" in response_json["Attribute"]
        assert "distribution" in response_json["Attribute"]
        assert "sharing_group_id" in response_json["Attribute"]
        assert "comment" in response_json["Attribute"]
        assert "deleted" in response_json["Attribute"]
        assert "disable_correlation" in response_json["Attribute"]
        assert "first_seen" in response_json["Attribute"]
        assert "last_seen" in response_json["Attribute"]
        assert "event_uuid" in response_json["Attribute"]
        assert "tag" in response_json["Attribute"]
        if len(response_json["Attribute"]["tag"]) > 0:
            assert response_json["Attribute"]["tag"][0]["id"] == str(tag_id)

    def test_get_invalid_or_non_existing_attribute(
        self: "TestGetAttributeDetails", invalid_or_non_existing_ids: Any
    ) -> None:
        response = client.get(f"/attributes/{invalid_or_non_existing_ids}")
        assert response.status_code == 404

    def test_get_attribute_response_format(self: "TestGetAttributeDetails", existing_id: str) -> None:
        response = client.get(f"/attributes/{existing_id}")
        assert response.headers["Content-Type"] == "application/json"


# --- Test edit attribute


class TestEditAttribute:
    def test_edit_existing_attribute(
        self: "TestEditAttribute", db: Session, existing_id: str, edit_attribute_valid_data: Dict[str, Any]
    ) -> None:
        add_event_body = Event(info="test")

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = str(add_event_body.id)

        add_attribute_body = Attribute(
            value="1.2.3.4", value1="1.2.3.4", type="ip-src", category="Network Activity", event_id=event_id
        )

        db.add(add_attribute_body)
        db.commit()
        db.refresh(add_attribute_body)

        attribute_id = add_attribute_body.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.put(f"/attributes/{attribute_id}", json=edit_attribute_valid_data, headers=headers)

        assert response.status_code == 200
        response_json = response.json()

        assert response_json["Attribute"]["id"] == str(attribute_id)
        assert response_json["Attribute"]["event_id"] == str(event_id)
        assert "id" in response_json["Attribute"]
        assert "event_id" in response_json["Attribute"]
        assert "object_id" in response_json["Attribute"]
        assert "object_relation" in response_json["Attribute"]
        assert "category" in response_json["Attribute"]
        assert "type" in response_json["Attribute"]
        assert "value" in response_json["Attribute"]
        assert "to_ids" in response_json["Attribute"]
        assert "uuid" in response_json["Attribute"]
        assert "timestamp" in response_json["Attribute"]
        assert "distribution" in response_json["Attribute"]
        assert "sharing_group_id" in response_json["Attribute"]
        assert "comment" in response_json["Attribute"]
        assert "deleted" in response_json["Attribute"]
        assert "disable_correlation" in response_json["Attribute"]
        assert "first_seen" in response_json["Attribute"]
        assert "last_seen" in response_json["Attribute"]
        assert "tag" in response_json["Attribute"]

    def test_edit_non_existing_attribute(
        self: "TestEditAttribute", invalid_or_non_existing_ids: Any, edit_attribute_valid_data: Dict[str, Any]
    ) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.put(
            f"/attributes/{invalid_or_non_existing_ids}", json=edit_attribute_valid_data, headers=headers
        )
        assert response.status_code == 404

    def test_edit_attribute_response_format(
        self: "TestEditAttribute", existing_id: str, edit_attribute_valid_data: Dict[str, Any]
    ) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.put(f"/attributes/{existing_id}", json=edit_attribute_valid_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"

    def test_edit_attribute_authorization(
        self: "TestEditAttribute", existing_id: str, edit_attribute_valid_data: Dict[str, Any]
    ) -> None:
        headers = {"authorization": ""}
        response = client.put(f"/attributes/{existing_id}", json=edit_attribute_valid_data, headers=headers)
        assert response.status_code == 401


# --- Test delete attribute by id


class TestDeleteAttribute:
    def test_delete_existing_attribute(self: "TestDeleteAttribute", db: Session) -> None:
        add_event_body = Event(info="test")

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = str(add_event_body.id)

        add_attribute_body = Attribute(
            value="1.2.3.4", value1="1.2.3.4", type="ip-src", category="Network Activity", event_id=event_id
        )

        db.add(add_attribute_body)
        db.commit()
        db.refresh(add_attribute_body)

        attribute_id = add_attribute_body.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/attributes/{attribute_id}", headers=headers)

        assert response.status_code == 200

    def test_delete_invalid_or_non_existing_attribute(
        self: "TestDeleteAttribute", invalid_or_non_existing_ids: Any
    ) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/attributes/{invalid_or_non_existing_ids}", headers=headers)
        assert response.status_code == 404

    def test_delete_attribute_response_format(self: "TestDeleteAttribute", existing_id: str) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/attributes/{existing_id}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"

    def test_delete_attribute_authorization(self: "TestDeleteAttribute", existing_id: str) -> None:
        headers = {"authorization": ""}
        response = client.delete(f"/attributes/{existing_id}", headers=headers)
        assert response.status_code == 401


# --- Test get all attributes


class TestGetAllAttributes:
    def test_get_all_attributes(self: "TestGetAllAttributes", db: Session) -> None:
        add_event_body = Event(info="test")

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = str(add_event_body.id)

        add_attribute_body1 = Attribute(
            value="test", value1="test", type="text", category="Network Activity", event_id=event_id
        )

        db.add(add_attribute_body1)
        db.commit()
        db.refresh(add_attribute_body1)

        add_attribute_body2 = Attribute(
            value="1.2.3.4", value1="1.2.3.4", type="ip-src", category="Network Activity", event_id=event_id
        )

        db.add(add_attribute_body2)
        db.commit()
        db.refresh(add_attribute_body2)

        response = client.get("/attributes")

        assert response.status_code == 200
        response_json = response.json()
        for attribute in response_json:
            assert isinstance(response_json, list)
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

    def test_get_all_attributes_response_format(
        self: "TestGetAllAttributes",
    ) -> None:
        response = client.get("/attributes")
        assert response.headers["Content-Type"] == "application/json"


# --- Test delete selected attribute(s)


class TestDeleteSelectedAttributes:
    def test_delete_selected_attributes_from_existing_event(
        self: "TestDeleteSelectedAttributes", db: Session, delete_selected_existing_attributes_data: Dict[str, Any]
    ) -> None:
        add_event_body = Event(info="test")

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = str(add_event_body.id)

        add_attribute_body1 = Attribute(
            value="test", value1="test", type="text", category="Network Activity", event_id=event_id
        )

        db.add(add_attribute_body1)
        db.commit()
        db.refresh(add_attribute_body1)

        attribute_id1 = add_attribute_body1.id

        add_attribute_body2 = Attribute(
            value="1.2.3.4", value1="1.2.3.4", type="ip-src", category="Network Activity", event_id=event_id
        )

        db.add(add_attribute_body2)
        db.commit()
        db.refresh(add_attribute_body2)

        attribute_id2 = add_attribute_body2.id

        attribute_ids = str(attribute_id1) + " " + str(attribute_id2)

        delete_selected_existing_attributes_data["id"] = attribute_ids

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            f"/attributes/deleteSelected/{event_id}", json=delete_selected_existing_attributes_data, headers=headers
        )

        assert response.status_code == 200
        response_json = response.json()
        counter_of_selected_attributes = len(attribute_ids)
        if counter_of_selected_attributes == 1:
            assert response_json["message"] == "1 attribute deleted."
        else:
            assert response_json["message"] == "2 attributes deleted."
        assert response_json["url"] == f"/attributes/deleteSelected/{event_id}"

    def test_delete_selected_attributes_response_format(
        self: "TestDeleteSelectedAttributes", existing_id: str, delete_selected_existing_attributes_data: Dict[str, Any]
    ) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            f"/attributes/deleteSelected/{existing_id}", json=delete_selected_existing_attributes_data, headers=headers
        )
        assert response.headers["Content-Type"] == "application/json"

    def test_delete_selected_attributes_authorization(
        self: "TestDeleteSelectedAttributes", existing_id: str, delete_selected_existing_attributes_data: Dict[str, Any]
    ) -> None:
        headers = {"authorization": ""}
        response = client.post(
            f"/attributes/deleteSelected/{existing_id}", json=delete_selected_existing_attributes_data, headers=headers
        )
        assert response.status_code == 401


# class TestAttributesRestSearch:
#
# def test_valid_search_attribute_data(search_attribute_valid_data: Dict[str, Any]) -> None:
#     headers = {"authorization": environment.site_admin_user_token}
#     response = client.post("/attributes/restSearch", json=search_attribute_valid_data, headers=headers)
#     assert response.status_code == 200
#     response_json = response.json()
#     assert response_json[0] == "response"
#     response_json_attribute = response_json["response"][0]
#     assert response_json_attribute == "Attribute"
#     response_json_details = response_json_attribute["Attribute"][0]
#     for key, value in search_attribute_valid_data:
#         assert response_json_details[key] == value
#
#
# def test_invalid_search_attribute_data(
#         search_attributes_invalid_data: Dict[str, Any],
# ) -> None:
#     headers = {"authorization": environment.site_admin_user_token}
#     response = client.post("/attributes/restSearch", json=search_attributes_invalid_data, headers=headers)
#     assert response.status_code == 404
#
#
# def test_search_attributes_response_format(search_attribute_valid_data: Dict[str, Any]) -> None:
#     headers = {"authorization": environment.site_admin_user_token}
#     response = client.post("/attributes/restSearch", json=search_attribute_valid_data, headers=headers)
#     assert response.headers["Content-Type"] == "application/json"
#
#
# def test_search_attributes_authorization(search_attribute_valid_data: Dict[str, Any]) -> None:
#     headers = {"authorization": ""}
#     response = client.post("/attributes/restSearch", json=search_attribute_valid_data, headers=headers)
#     assert response.status_code == 401
#
#
# # --- Test attribute statistics


class TestAttributeStatistics:
    def test_valid_parameters_attribute_statistics(
        self: "TestAttributeStatistics", valid_parameters_attribute_statistics: Dict[str, Any]
    ) -> None:
        context = valid_parameters_attribute_statistics["context"]
        percentage = valid_parameters_attribute_statistics["percentage"]
        response = client.get(f"/attributes/attributeStatistics/{context}/{percentage}")
        assert response.status_code == 200
        response_json = response.json()
        print(response_json)
        if context == "category":
            for category in GetDescribeTypesAttributes().categories:
                assert category in response_json
        else:
            for type in GetDescribeTypesAttributes().types:
                assert type in response_json
        if percentage == 1:
            for item in response_json:
                assert "%" in item

    def test_invalid_parameters_attribute_statistics(
        self: "TestAttributeStatistics", invalid_parameters_attribute_statistics: Dict[str, Any]
    ) -> None:
        context = invalid_parameters_attribute_statistics["context"]
        percentage = invalid_parameters_attribute_statistics["percentage"]
        response = client.get(f"/attributes/attributeStatistics/{context}/{percentage}")
        assert response.status_code == 405

    def test_attribute_statistics_response_format(
        self: "TestAttributeStatistics", valid_parameters_attribute_statistics: Dict[str, Any]
    ) -> None:
        context = valid_parameters_attribute_statistics["context"]
        percentage = valid_parameters_attribute_statistics["percentage"]
        response = client.get(f"/attributes/attributeStatistics/{context}/{percentage}")
        assert response.headers["Content-Type"] == "application/json"


# --- Test attribute describe types


class TestAttributeDescribeTypes:
    def test_attribute_describe_types(self: "TestAttributeDescribeTypes") -> None:
        response = client.get("/attributes/describeTypes")
        response_json = response.json()
        print(response_json)
        assert response.status_code == 200

    def test_attribute_describe_types_response_format(self: "TestAttributeDescribeTypes") -> None:
        response = client.get("/attributes/describeTypes")
        assert response.headers["Content-Type"] == "application/json"
        response_json = response.json()
        assert "types" in response_json["result"]
        assert "md5" in response_json["result"]["types"]


# --- Test restore attribute


class TestRestoreAttribute:
    def test_restore_existing_attribute(self: "TestRestoreAttribute", db: Session) -> None:
        add_event_body = Event(info="test")

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = str(add_event_body.id)

        add_attribute_body = Attribute(
            value="1.2.3.4", value1="1.2.3.4", type="ip-src", category="Network Activity", event_id=event_id
        )

        db.add(add_attribute_body)
        db.commit()
        db.refresh(add_attribute_body)

        attribute_id = add_attribute_body.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/attributes/restore/{attribute_id}", headers=headers)
        assert response.status_code == 200

    def test_restore_invalid_attribute(self: "TestRestoreAttribute", invalid_or_non_existing_ids: Any) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/attributes/restore/{invalid_or_non_existing_ids}", headers=headers)
        assert response.status_code == 404

    def test_restore_attribute_response_format(self: "TestRestoreAttribute", existing_id: str) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/attributes/restore/{existing_id}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"

    def test_restore_attribute_authorization(self: "TestRestoreAttribute", existing_id: str) -> None:
        headers = {"authorization": ""}
        response = client.post(f"/attributes/restore/{existing_id}", headers=headers)
        assert response.status_code == 401


# --- Test adding a tag


class TestAddTagToAttribute:
    def test_add_existing_tag_to_attribute(
        self: "TestAddTagToAttribute", db: Session, existing_id: str, valid_local_add_tag_to_attribute: int
    ) -> None:
        add_event_body = Event(info="test")

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = str(add_event_body.id)

        add_attribute_body = Attribute(
            value="1.2.3.4", value1="1.2.3.4", type="ip-src", category="Network Activity", event_id=event_id
        )

        db.add(add_attribute_body)
        db.commit()
        db.refresh(add_attribute_body)

        attribute_id = add_attribute_body.id

        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(100001, 200000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            is_galaxy=False,
            is_custom_galaxy=False,
            attribute_count=1,
            count=1,
            favourite=False,
            local_only=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_id = add_tag_body.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            f"/attributes/addTag/{attribute_id}/{tag_id}/local:{valid_local_add_tag_to_attribute}",
            headers=headers,
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["saved"] is True
        assert response_json["success"] == "Tag added"
        assert response_json["check_publish"] is True

    def test_add_invalid_or_non_existing_tag_to_attribute(
        self: "TestAddTagToAttribute",
        db: Session,
        existing_id: str,
        invalid_or_non_existing_ids: Any,
        valid_local_add_tag_to_attribute: int,
    ) -> None:
        add_event_body = Event(info="test")

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = str(add_event_body.id)

        add_attribute_body = Attribute(
            value="1.2.3.4", value1="1.2.3.4", type="ip-src", category="Network Activity", event_id=event_id
        )

        db.add(add_attribute_body)
        db.commit()
        db.refresh(add_attribute_body)

        attribute_id = add_attribute_body.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            f"/attributes/addTag/{attribute_id}/{invalid_or_non_existing_ids}/local:{valid_local_add_tag_to_attribute}",
            headers=headers,
        )
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["saved"] is False

    def test_add_tag_to_attribute_response_format(
        self: "TestAddTagToAttribute", existing_id: str, valid_local_add_tag_to_attribute: int
    ) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            f"/attributes/addTag/{existing_id}/{existing_id}/local:{valid_local_add_tag_to_attribute}",
            headers=headers,
        )
        assert response.headers["Content-Type"] == "application/json"

    def test_add_tag_to_attribute_authorization(
        self: "TestAddTagToAttribute", existing_id: str, valid_local_add_tag_to_attribute: int
    ) -> None:
        headers = {"authorization": ""}
        response = client.post(
            f"/attributes/addTag/{existing_id}/{existing_id}/local:{valid_local_add_tag_to_attribute}",
            headers=headers,
        )
        assert response.status_code == 401


class TestRemoveTagFromAttribute:
    def test_remove_existing_tag_from_attribute(self: "TestRemoveTagFromAttribute", db: Session) -> None:
        add_event_body = Event(info="test")

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = str(add_event_body.id)

        add_attribute_body = Attribute(
            value="1.2.3.4", value1="1.2.3.4", type="ip-src", category="Network Activity", event_id=event_id
        )

        db.add(add_attribute_body)
        db.commit()
        db.refresh(add_attribute_body)

        attribute_id = add_attribute_body.id

        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(200001, 300000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            is_galaxy=False,
            is_custom_galaxy=False,
            attribute_count=1,
            count=1,
            favourite=False,
            local_only=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_id = add_tag_body.id

        add_attribute_tag_body = AttributeTag(attribute_id=attribute_id, event_id=event_id, tag_id=tag_id, local=False)

        db.add(add_attribute_tag_body)
        db.commit()
        db.refresh(add_attribute_tag_body)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/attributes/removeTag/{attribute_id}/{tag_id}", headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["saved"] is True
        assert response_json["success"] == "Tag removed"

    def test_remove_tag_from_attribute_response_format(self: "TestRemoveTagFromAttribute", existing_id: str) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/attributes/removeTag/{existing_id}/{existing_id}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"

    def test_remove_tag_from_attribute(self: "TestRemoveTagFromAttribute", existing_id: str) -> None:
        headers = {"authorization": ""}
        response = client.post(f"/attributes/removeTag/{existing_id}/{existing_id}", headers=headers)
        assert response.status_code == 401
