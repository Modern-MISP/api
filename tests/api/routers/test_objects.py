from datetime import datetime
from typing import Any

import pytest
from sqlalchemy.orm import Session

from mmisp.db.models.event import Event
from mmisp.db.models.object import ObjectTemplate
from tests.environment import client, environment
from tests.generators.model_generators.sharing_group_generator import generate_sharing_group
from tests.generators.object_generator import (
    generate_random_search_query,
    generate_search_query,
    generate_specific_search_query,
    generate_valid_object_data,
    generate_valid_random_object_data,
)


@pytest.fixture(
    params=[
        generate_valid_object_data().dict(),
        generate_valid_random_object_data().dict(),
        generate_valid_random_object_data().dict(),
        generate_valid_random_object_data().dict(),
        generate_valid_random_object_data().dict(),
    ]
)
def object_data(request: Any) -> dict[str, Any]:
    return request.param


class TestAddObject:
    @staticmethod
    def test_add_object_to_event(object_data: dict[str, Any], db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        object_data["sharing_group_id"] = sharing_group.id
        for attribute in object_data["attributes"]:
            attribute["sharing_group_id"] = sharing_group.id

        object_template = ObjectTemplate(name="test_template", user_id=1, org_id=1, version=100)
        db.add(object_template)
        db.flush()
        db.refresh(object_template)

        event = Event(
            user_id=environment.instance_owner_org_admin_user.id,
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis=0,
            sharing_group_id=object_data["sharing_group_id"],
            threat_level_id=0,
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        object_data["event_id"] = event.id

        db.commit()

        object_template_id = object_template.id
        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
        assert response.status_code == 201

        response_data = response.json()
        assert "object" in response_data
        assert int(response_data["object"]["event_id"]) == event_id

    @staticmethod
    def test_add_object_response_format(object_data: dict[str, Any], db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        object_data["sharing_group_id"] = sharing_group.id
        for attribute in object_data["attributes"]:
            attribute["sharing_group_id"] = sharing_group.id

        object_template = ObjectTemplate(name="test_template", user_id=1, org_id=1, version=100)
        db.add(object_template)
        db.flush()
        db.refresh(object_template)

        event = Event(
            user_id=environment.instance_owner_org_admin_user.id,
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis=0,
            sharing_group_id=object_data["sharing_group_id"],
            threat_level_id=0,
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        object_data["event_id"] = event.id

        db.commit()

        object_template_id = object_template.id
        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        assert "object" in response.json()


@pytest.fixture(
    params=[
        generate_specific_search_query().dict(),
        generate_search_query().dict(),
        generate_random_search_query().dict(),
        generate_random_search_query().dict(),
    ]
)
def search_data(request: Any) -> dict[str, Any]:
    return request.param


class TestSearchObject:
    @staticmethod
    def test_search_objects_with_filters(search_data: dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/objects/restsearch", json=search_data, headers=headers)
        assert response.status_code == 200

        response_data = response.json()
        assert "response" in response_data
        assert isinstance(response_data["response"], list)
        for obj in response_data["response"]:
            assert "id" in obj["object"] != ""
            assert "name" in obj["object"] != ""
            assert "sharing_group_id" in obj["object"] != ""
            assert "distribution" in obj["object"] != ""
            assert "comment" in obj["object"] != ""

    @staticmethod
    def test_search_objects_response_format(search_data: dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/objects/restsearch", json=search_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        response_data = response.json()
        assert "response" in response_data
        assert isinstance(response_data["response"], list)

    @staticmethod
    def test_search_objects_data_integrity(search_data: dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/objects/restsearch", json=search_data, headers=headers)
        response_data = response.json()
        for obj in response_data["response"]:
            assert "id" in obj["object"] != ""
            assert "name" in obj["object"] != ""
            assert "meta_category" in obj["object"] != ""
            assert "distribution" in obj["object"] != ""


class TestGetObjectInfo:
    @staticmethod
    def test_get_object_details_valid_id(object_data: dict[str, Any], db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        object_data["sharing_group_id"] = sharing_group.id
        for attribute in object_data["attributes"]:
            attribute["sharing_group_id"] = sharing_group.id

        object_template = ObjectTemplate(name="test_template", user_id=1, org_id=1, version=100)
        db.add(object_template)
        db.flush()
        db.refresh(object_template)

        event = Event(
            user_id=environment.instance_owner_org_admin_user.id,
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis=0,
            sharing_group_id=object_data["sharing_group_id"],
            threat_level_id=0,
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        object_data["event_id"] = event.id

        db.commit()

        object_template_id = object_template.id
        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
        assert response.status_code == 201

        response_data = response.json()
        object_id = response_data["object"]["id"]
        response = client.get(f"/objects/{object_id}", headers=headers)
        assert response.status_code == 200

        response_data = response.json()
        assert "object" in response_data
        object_data = response_data["object"]
        assert object_data["id"] == object_id
        assert "name" in object_data
        assert "meta_category" in object_data
        assert "distribution" in object_data
        assert "comment" in object_data
        assert "sharing_group_id" in object_data

    @staticmethod
    def test_get_object_details_response_format(object_data: dict[str, Any], db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        object_data["sharing_group_id"] = sharing_group.id
        for attribute in object_data["attributes"]:
            attribute["sharing_group_id"] = sharing_group.id

        object_template = ObjectTemplate(name="test_template", user_id=1, org_id=1, version=100)
        db.add(object_template)
        db.flush()
        db.refresh(object_template)

        event = Event(
            user_id=environment.instance_owner_org_admin_user.id,
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis=0,
            sharing_group_id=object_data["sharing_group_id"],
            threat_level_id=0,
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        object_data["event_id"] = event.id

        db.commit()

        object_template_id = object_template.id
        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
        assert response.status_code == 201

        response_data = response.json()
        object_id = response_data["object"]["id"]
        response = client.get(f"/objects/{object_id}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        response_data = response.json()
        assert "object" in response_data

    @staticmethod
    def test_get_object_details_invalid_id() -> None:
        object_id: str = "invalid_id"
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/objects/{object_id}", headers=headers)
        assert response.status_code == 422

    @staticmethod
    def test_get_object_details_data_integrity(object_data: dict[str, Any], db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        object_data["sharing_group_id"] = sharing_group.id
        for attribute in object_data["attributes"]:
            attribute["sharing_group_id"] = sharing_group.id

        object_template = ObjectTemplate(name="test_template", user_id=1, org_id=1, version=100)
        db.add(object_template)
        db.flush()
        db.refresh(object_template)

        event = Event(
            user_id=environment.instance_owner_org_admin_user.id,
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis=0,
            sharing_group_id=object_data["sharing_group_id"],
            threat_level_id=0,
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        object_data["event_id"] = event.id

        db.commit()

        object_template_id = object_template.id
        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
        assert response.status_code == 201

        response_data = response.json()
        object_id = response_data["object"]["id"]
        response = client.get(f"/objects/{object_id}", headers=headers)
        response_data = response.json()
        object_data = response_data["object"]
        assert isinstance(object_data["id"], str)
        assert isinstance(object_data["name"], str)


class TestDeleteObject:
    @staticmethod
    def test_delete_object_hard_delete(object_data: dict[str, Any], db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        object_data["sharing_group_id"] = sharing_group.id
        for attribute in object_data["attributes"]:
            attribute["sharing_group_id"] = sharing_group.id

        object_template = ObjectTemplate(name="test_template", user_id=1, org_id=1, version=100)
        db.add(object_template)
        db.flush()
        db.refresh(object_template)

        event = Event(
            user_id=environment.instance_owner_org_admin_user.id,
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis=0,
            sharing_group_id=object_data["sharing_group_id"],
            threat_level_id=0,
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        object_data["event_id"] = event.id

        db.commit()

        object_template_id = object_template.id
        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
        assert response.status_code == 201

        response_data = response.json()
        object_id = response_data["object"]["id"]
        response = client.delete(f"/objects/{object_id}/true", headers=headers)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["message"] == "Object has been permanently deleted."
        assert response_data["name"] == object_data["name"]
        assert response_data["saved"]
        assert response_data["success"]

    @staticmethod
    def test_delete_object_soft_delete(object_data: dict[str, Any], db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        object_data["sharing_group_id"] = sharing_group.id
        for attribute in object_data["attributes"]:
            attribute["sharing_group_id"] = sharing_group.id

        object_template = ObjectTemplate(name="test_template", user_id=1, org_id=1, version=100)
        db.add(object_template)
        db.flush()
        db.refresh(object_template)

        event = Event(
            user_id=environment.instance_owner_org_admin_user.id,
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis=0,
            sharing_group_id=object_data["sharing_group_id"],
            threat_level_id=0,
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        object_data["event_id"] = event.id

        db.commit()

        object_template_id = object_template.id
        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
        assert response.status_code == 201

        response_data = response.json()
        object_id = response_data["object"]["id"]
        response_delete = client.delete(f"/objects/{object_id}/false", headers=headers)
        assert response_delete.status_code == 200

        response_data = response_delete.json()
        assert response_data["message"] == "Object has been soft deleted."
        assert response_data["name"] == object_data["name"]
        assert response_data["saved"]
        assert response_data["success"]

    @staticmethod
    def test_delete_object_invalid_id() -> None:
        object_id = "invalid_id"
        headers = {"authorization": environment.site_admin_user_token}
        response_delete = client.delete(f"/objects/{object_id}/true", headers=headers)
        assert response_delete.status_code == 422
        assert "detail" in response_delete.json()

    @staticmethod
    def test_delete_object_invalid_hard_delete(object_data: dict[str, Any], db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        object_data["sharing_group_id"] = sharing_group.id
        for attribute in object_data["attributes"]:
            attribute["sharing_group_id"] = sharing_group.id

        object_template = ObjectTemplate(name="test_template", user_id=1, org_id=1, version=100)
        db.add(object_template)
        db.flush()
        db.refresh(object_template)

        event = Event(
            user_id=environment.instance_owner_org_admin_user.id,
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis=0,
            sharing_group_id=object_data["sharing_group_id"],
            threat_level_id=0,
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        object_data["event_id"] = event.id

        db.commit()

        object_template_id = object_template.id
        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
        assert response.status_code == 201

        response_data = response.json()
        object_id = response_data["object"]["id"]
        response_delete = client.delete(f"/objects/{object_id}/invalid_value", headers=headers)
        assert response_delete.status_code == 422
        assert "detail" in response_delete.json()
