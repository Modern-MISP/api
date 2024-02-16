import time
from typing import Any

import pytest

from mmisp.db.models.event import Event
from mmisp.db.models.object import ObjectTemplate
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.sharing_group import SharingGroup
from tests.environment import client, environment, get_db
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
    def test_add_object_to_event(self: "TestAddObject", object_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
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

        organisation = Organisation(
            name="test",
            date_created=str(int(time.time())),
            date_modified=str(int(time.time())),
        )
        db.add(organisation)
        db.flush()
        db.refresh(organisation)

        event = Event(
            org_id=organisation.id,
            orgc_id=organisation.id,
            info="test",
            date=str(int(time.time())),
            analysis="test",
            event_creator_email="XXXXXXXXXXXXX",
        )
        db.add(event)
        db.flush()
        db.refresh(event)

        db.commit()

        object_template_id = object_template.id
        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
        assert response.status_code == 201

        response_data = response.json()
        assert "object" in response_data
        assert int(response_data["object"]["event_id"]) == event_id
        assert int(response_data["object"]["template_id"]) == object_template_id

    def test_add_object_response_format(self: "TestAddObject", object_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
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

        organisation = Organisation(
            name="test",
            date_created=str(int(time.time())),
            date_modified=str(int(time.time())),
        )
        db.add(organisation)
        db.flush()
        db.refresh(organisation)

        event = Event(
            org_id=organisation.id,
            orgc_id=organisation.id,
            info="test",
            date=str(int(time.time())),
            analysis="test",
            event_creator_email="XXXXXXXXXXXXX",
        )
        db.add(event)
        db.flush()
        db.refresh(event)

        db.commit()

        object_template_id = object_template.id
        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        assert "object" in response.json()

    def test_add_object_to_event_authorization(self: "TestAddObject", object_data: dict[str, Any]) -> None:
        headers = {"authorization": ""}
        response = client.post("/feeds", json=object_data, headers=headers)
        assert response.status_code == 401


@pytest.fixture(
    params=[
        generate_specific_search_query().dict(),
        generate_search_query().dict(),
        generate_random_search_query().dict(),
        generate_random_search_query().dict(),
        generate_random_search_query().dict(),
        generate_random_search_query().dict(),
    ]
)
def search_data(request: Any) -> dict[str, Any]:
    return request.param


class TestSearchObject:
    def test_search_objects_with_filters(self: "TestSearchObject", search_data: dict[str, Any]) -> None:
        response = client.post("/objects/restsearch", json=search_data)
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

    def test_search_objects_response_format(self: "TestSearchObject", search_data: dict[str, Any]) -> None:
        response = client.post("/objects/restsearch", json=search_data)
        assert response.headers["Content-Type"] == "application/json"
        response_data = response.json()
        assert "response" in response_data
        assert isinstance(response_data["response"], list)

    def test_search_objects_data_integrity(self: "TestSearchObject", search_data: dict[str, Any]) -> None:
        response = client.post("/objects/restsearch", json=search_data)
        response_data = response.json()
        for obj in response_data["response"]:
            assert "id" in obj["object"] != ""
            assert "name" in obj["object"] != ""
            assert "meta_category" in obj["object"] != ""
            assert "distribution" in obj["object"] != ""


class TestGetObjectInfo:
    def test_get_object_details_valid_id(self: "TestGetObjectInfo", object_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
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

        organisation = Organisation(
            name="test",
            date_created=str(int(time.time())),
            date_modified=str(int(time.time())),
        )
        db.add(organisation)
        db.flush()
        db.refresh(organisation)

        event = Event(
            org_id=organisation.id,
            orgc_id=organisation.id,
            info="test",
            date=str(int(time.time())),
            analysis="test",
            event_creator_email="XXXXXXXXXXXXX",
        )
        db.add(event)
        db.flush()
        db.refresh(event)

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

    def test_get_object_details_response_format(self: "TestGetObjectInfo", object_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
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

        organisation = Organisation(
            name="test",
            date_created=str(int(time.time())),
            date_modified=str(int(time.time())),
        )
        db.add(organisation)
        db.flush()
        db.refresh(organisation)

        event = Event(
            org_id=organisation.id,
            orgc_id=organisation.id,
            info="test",
            date=str(int(time.time())),
            analysis="test",
            event_creator_email="XXXXXXXXXXXXX",
        )
        db.add(event)
        db.flush()
        db.refresh(event)

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

    def test_get_object_details_invalid_id(self: "TestGetObjectInfo") -> None:
        object_id: str = "invalid_id"
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/objects/{object_id}", headers=headers)
        assert response.status_code == 404

    def test_get_object_details_data_integrity(self: "TestGetObjectInfo", object_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
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

        organisation = Organisation(
            name="test",
            date_created=str(int(time.time())),
            date_modified=str(int(time.time())),
        )
        db.add(organisation)
        db.flush()
        db.refresh(organisation)

        event = Event(
            org_id=organisation.id,
            orgc_id=organisation.id,
            info="test",
            date=str(int(time.time())),
            analysis="test",
            event_creator_email="XXXXXXXXXXXXX",
        )
        db.add(event)
        db.flush()
        db.refresh(event)

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
    def test_delete_object_hard_delete(self: "TestDeleteObject", object_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
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

        organisation = Organisation(
            name="test",
            date_created=str(int(time.time())),
            date_modified=str(int(time.time())),
        )
        db.add(organisation)
        db.flush()
        db.refresh(organisation)

        event = Event(
            org_id=organisation.id,
            orgc_id=organisation.id,
            info="test",
            date=str(int(time.time())),
            analysis="test",
            event_creator_email="XXXXXXXXXXXXX",
        )
        db.add(event)
        db.flush()
        db.refresh(event)

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
        assert response_data["saved"] is True
        assert response_data["success"] is True

    def test_delete_object_soft_delete(self: "TestDeleteObject", object_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
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

        organisation = Organisation(
            name="test",
            date_created=str(int(time.time())),
            date_modified=str(int(time.time())),
        )
        db.add(organisation)
        db.flush()
        db.refresh(organisation)

        event = Event(
            org_id=organisation.id,
            orgc_id=organisation.id,
            info="test",
            date=str(int(time.time())),
            analysis="test",
            event_creator_email="XXXXXXXXXXXXX",
        )
        db.add(event)
        db.flush()
        db.refresh(event)

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
        assert response_data["saved"] is True
        assert response_data["success"] is True

    def test_delete_object_invalid_id(self: "TestDeleteObject") -> None:
        object_id = "invalid_id"
        headers = {"authorization": environment.site_admin_user_token}
        response_delete = client.delete(f"/objects/{object_id}/true", headers=headers)
        assert response_delete.status_code == 404
        assert "detail" in response_delete.json()

    def test_delete_object_invalid_hard_delete(self: "TestDeleteObject", object_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
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

        organisation = Organisation(
            name="test",
            date_created=str(int(time.time())),
            date_modified=str(int(time.time())),
        )
        db.add(organisation)
        db.flush()
        db.refresh(organisation)

        event = Event(
            org_id=organisation.id,
            orgc_id=organisation.id,
            info="test",
            date=str(int(time.time())),
            analysis="test",
            event_creator_email="XXXXXXXXXXXXX",
        )
        db.add(event)
        db.flush()
        db.refresh(event)

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

    def test_delete_object_no_authorization(self: "TestDeleteObject", object_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
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

        organisation = Organisation(
            name="test",
            date_created=str(int(time.time())),
            date_modified=str(int(time.time())),
        )
        db.add(organisation)
        db.flush()
        db.refresh(organisation)

        event = Event(
            org_id=organisation.id,
            orgc_id=organisation.id,
            info="test",
            date=str(int(time.time())),
            analysis="test",
            event_creator_email="XXXXXXXXXXXXX",
        )
        db.add(event)
        db.flush()
        db.refresh(event)

        db.commit()

        object_template_id = object_template.id
        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
        assert response.status_code == 201

        response_data = response.json()
        object_id = response_data["object"]["id"]
        response_delete = client.delete(f"/objects/{object_id}/true")
        assert response_delete.status_code == 401
        assert "detail" in response_delete.json()
