from datetime import datetime
from random import Random
from typing import Any, Dict

import pytest
from sqlalchemy.orm import Session

from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event, EventTag
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.tag import Tag

from ...environment import client, environment, get_db
from ...generators.event_generator import (
    generate_invalid_add_event_body,
    generate_invalid_id,
    generate_invalid_update_event_body,
    generate_non_existing_id,
    generate_valid_add_attribute_via_free_text_import_body,
    generate_valid_add_event_body,
    generate_valid_local_add_tag_to_event,
    generate_valid_update_event_body,
)


@pytest.fixture(scope="function")
def db() -> Session:
    db_session = get_db()

    yield db_session

    db_session.close()


@pytest.fixture(scope="module")
def add_event_valid_data() -> Dict[str, Any]:
    return generate_valid_add_event_body().dict()


@pytest.fixture(scope="module")
def add_event_invalid_data() -> Dict[str, Any]:
    return generate_invalid_add_event_body().dict()


@pytest.fixture(params=[generate_non_existing_id(), generate_invalid_id()], scope="module")
def invalid_ids(request: Any) -> Dict[str, Any]:
    return request.param


@pytest.fixture(scope="module")
def valid_update_event_data() -> Dict[str, Any]:
    return generate_valid_update_event_body().dict()


@pytest.fixture(scope="module")
def invalid_update_event_data() -> Dict[str, Any]:
    return generate_invalid_update_event_body().dict()


@pytest.fixture(scope="module")
def valid_local_add_tag_to_event() -> str:
    return generate_valid_local_add_tag_to_event()


@pytest.fixture(scope="module")
def add_attribute_via_free_text_import_valid_data() -> Dict[str, Any]:
    return generate_valid_add_attribute_via_free_text_import_body()


class TestAddEvent:
    def test_add_event_valid_data(self: "TestAddEvent", add_event_valid_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events", json=add_event_valid_data, headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["Event"]["info"] == add_event_valid_data["info"]
        assert "id" in response_json["Event"]["Org"]
        assert "name" in response_json["Event"]["Org"]
        assert "uuid" in response_json["Event"]["Org"]
        assert "local" in response_json["Event"]["Org"]

    def test_add_event_invalid_data(self: "TestAddEvent", add_event_invalid_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events", json=add_event_invalid_data, headers=headers)

        if not add_event_invalid_data["info"]:
            assert response.status_code == 400
        elif not isinstance(add_event_invalid_data["info"], str):
            assert response.status_code == 403

    def test_add_event_response_format(self: "TestAddEvent", add_event_valid_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events", json=add_event_valid_data, headers=headers)

        assert response.headers["Content-Type"] == "application/json"

    def test_add_event_authorization(self: "TestAddEvent", add_event_valid_data: Dict[str, Any]) -> None:
        headers = {"authorization": ""}
        response = client.post("/events", json=add_event_valid_data, headers=headers)

        assert response.status_code == 401


class TestGetEventDetails:
    def test_get_existing_event(self: "TestGetEventDetails", db: Session) -> None:
        add_org_body = Organisation(name="test", local=True)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_event_body = Event(
            org_id=org_id,
            orgc_id=org_id,
            info="test event",
            date="2024-02-13",
            analysis="test analysis",
            event_creator_email="test@mail.de",
        )

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = add_event_body.id

        add_attribute_body = Attribute(value="test", value1="test", type="text", category="Other", event_id=event_id)

        db.add(add_attribute_body)
        db.commit()
        db.refresh(add_attribute_body)

        attribute_id = add_attribute_body.id

        add_galaxy_body = Galaxy(
            name="test galaxy",
            type="test type",
            description="test",
            version="version",
            kill_chain_order="test kill_chain_order",
        )

        db.add(add_galaxy_body)
        db.commit()
        db.refresh(add_galaxy_body)

        galaxy_id = add_galaxy_body.id

        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(300001, 400000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            inherited=False,
            is_galaxy=True,
            is_custom_galaxy=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_id = add_tag_body.id

        add_event_tag_body = EventTag(event_id=event_id, tag_id=tag_id, local=False)

        db.add(add_event_tag_body)
        db.commit()
        db.refresh(add_event_tag_body)

        add_galaxy_cluster_body = GalaxyCluster(
            collection_uuid="uuid",
            type="test type",
            value="test",
            tag_name=add_tag_body.name,
            description="test",
            galaxy_id=galaxy_id,
            authors="admin",
        )

        db.add(add_galaxy_cluster_body)
        db.commit()
        db.refresh(add_galaxy_cluster_body)

        galaxy_cluster_id = add_galaxy_cluster_body.id

        response = client.get(f"/events/{event_id}")

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["Event"]["id"] == str(event_id)
        assert response_json["Event"]["org_id"] == str(org_id)
        assert response_json["Event"]["orgc_id"] == str(org_id)
        assert response_json["Event"]["attribute_count"] == "1"
        assert response_json["Event"]["Attribute"][0]["id"] == str(attribute_id)
        assert response_json["Event"]["Tag"][0]["id"] == str(tag_id)
        assert response_json["Event"]["Galaxy"][0]["id"] == str(galaxy_id)
        assert response_json["Event"]["Galaxy"][0]["GalaxyCluster"][0]["id"] == str(galaxy_cluster_id)
        assert response_json["Event"]["Galaxy"][0]["GalaxyCluster"][0]["event_tag_id"] == str(add_event_tag_body.id)

    def test_get_non_existing_event(self: "TestGetEventDetails", db: Session, invalid_ids: str) -> None:
        response = client.get(f"/events/{invalid_ids}")

        assert response.status_code == 404

    def test_add_event_response_format(self: "TestGetEventDetails") -> None:
        response = client.get("/events/1")

        assert response.headers["Content-Type"] == "application/json"


class TestUpdateEvent:
    def test_update_existing_event(
        self: "TestUpdateEvent", db: Session, valid_update_event_data: Dict[str, Any]
    ) -> None:
        add_org_body = Organisation(name="test", local=True)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_event_body = Event(
            org_id=org_id,
            orgc_id=org_id,
            info="test event",
            date="2024-02-13",
            analysis="test analysis",
            event_creator_email="test@mail.de",
        )

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = add_event_body.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.put(f"events/{event_id}", json=valid_update_event_data, headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["Event"]["info"] == valid_update_event_data["info"]

    def test_update_non_existing_event(
        self: "TestGetEventDetails", db: Session, invalid_ids: str, valid_update_event_data: Dict[str, Any]
    ) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.put(f"/events/{invalid_ids}", json=valid_update_event_data, headers=headers)

        assert response.status_code == 404

    def test_update_event_response_format(self: "TestGetEventDetails") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.put("/events/1", headers=headers)

        assert response.headers["Content-Type"] == "application/json"

    def test_update_event_authorization(self: "TestAddEvent", add_event_valid_data: Dict[str, Any]) -> None:
        headers = {"authorization": ""}
        response = client.put("/events/1", json=add_event_valid_data, headers=headers)

        assert response.status_code == 401


class TestDeleteEvent:
    def test_delete_existing_event(self: "TestDeleteEvent", db: Session) -> None:
        add_org_body = Organisation(name="test", local=True)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_event_body = Event(
            org_id=org_id,
            orgc_id=org_id,
            info="test event",
            date="2024-02-13",
            analysis="test analysis",
            event_creator_email="test@mail.de",
        )

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = add_event_body.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"events/{event_id}", headers=headers)

        assert response.status_code == 200

    def test_delete_invalid_or_non_existing_event(self: "TestDeleteEvent", invalid_ids: Any) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/events/{invalid_ids}", headers=headers)

        assert response.status_code == 404

    def test_delete_event_response_format(self: "TestDeleteEvent") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete("/events/1", headers=headers)

        assert response.headers["Content-Type"] == "application/json"

    def test_delete_event_authorization(self: "TestDeleteEvent") -> None:
        headers = {"authorization": ""}
        response = client.delete("/events/1", headers=headers)

        assert response.status_code == 401


class TestGetAllEvents:
    def test_get_all_events(self: "TestGetAllEvents", db: Session) -> None:
        add_org_body = Organisation(name="test", local=True)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_event_body1 = Event(
            org_id=org_id,
            orgc_id=org_id,
            info="test event1",
            date="2024-02-13",
            analysis="test analysis",
            event_creator_email="test@mail.de",
        )

        db.add(add_event_body1)
        db.commit()
        db.refresh(add_event_body1)

        add_event_body2 = Event(
            org_id=org_id,
            orgc_id=org_id,
            info="test event2",
            date="2024-02-13",
            analysis="test analysis",
            event_creator_email="test@mail.de",
        )

        db.add(add_event_body2)
        db.commit()
        db.refresh(add_event_body2)

        response = client.get("/events")

        assert response.status_code == 200
        response_json = response.json()
        assert isinstance(response_json, list)

    def test_get_all_events_response_format(self: "TestGetAllEvents") -> None:
        response = client.get("/events")

        assert response.headers["Content-Type"] == "application/json"


class TestEventRestSearch:
    def test_valid_search_attribute_data(self: "TestEventRestSearch", db: Session) -> None:
        add_org_body = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
        )

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_event_body = Event(
            org_id=org_id,
            orgc_id=org_id,
            info="test event",
            date="2024-02-13",
            analysis="test analysis",
            event_creator_email="test@mail.de",
        )

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
        json = {"returnFormat": "json"}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events/restSearch", json=json, headers=headers)
        assert response.status_code == 200
        response_json = response.json()
        assert "response" in response_json
        assert isinstance(response_json["response"], list)
        response_json_attribute = response_json["response"][0]
        assert "Event" in response_json_attribute

    def test_invalid_search_attribute_data(self: "TestEventRestSearch") -> None:
        json = {"returnFormat": "invalid format"}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events/restSearch", json=json, headers=headers)
        assert response.status_code == 404


class TestIndexEvents:
    def test_index_events_valid_data(self: "TestIndexEvents", db: Session) -> None:
        add_org_body = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
        )

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_event_body = Event(
            org_id=org_id,
            orgc_id=org_id,
            info="test event",
            date="2024-02-13",
            analysis="test analysis",
            event_creator_email="test@mail.de",
            distribution=1,
        )

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        json = {"distribution": "1"}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events/index", json=json, headers=headers)
        assert response.status_code == 200
        response_json = response.json()
        assert isinstance(response_json, list)
        assert "id" in response_json[0]
        assert "GalaxyCluster" in response_json[0]


class TestPublishEvent:
    def test_publish_existing_event(self: "TestPublishEvent", db: Session) -> None:
        add_org_body = Organisation(name="test", local=True)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_event_body = Event(
            org_id=org_id,
            orgc_id=org_id,
            info="test event",
            date="2024-02-13",
            analysis="test analysis",
            event_creator_email="test@mail.de",
        )

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = add_event_body.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/events/publish/{event_id}", headers=headers)

        assert response.status_code == 200
        response_json = response.json()

        assert response_json["saved"] is True
        assert response_json["success"] is True
        assert response_json["name"] == "Job queued"
        assert response_json["message"] == "Job queued"
        assert response_json["url"] == f"/events/publish/{event_id}"
        assert response_json["id"] == str(event_id)

    def test_publish_invalid_event(self: "TestPublishEvent", invalid_ids: str) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/events/publish/{invalid_ids}", headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["name"] == "Invalid event."
        assert response_json["message"] == "Invalid event."
        assert response_json["url"] == f"/events/publish/{invalid_ids}"

    def test_publish_event_response_format(self: "TestPublishEvent") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events/publish/1", headers=headers)

        assert response.headers["Content-Type"] == "application/json"

    def test_publish_event_authorization(self: "TestPublishEvent") -> None:
        headers = {"authorization": ""}
        response = client.post("/events/publish/1", headers=headers)

        assert response.status_code == 401


class TestUnpublishEvent:
    def test_publish_existing_event(self: "TestUnpublishEvent", db: Session) -> None:
        add_org_body = Organisation(name="test", local=True)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_event_body = Event(
            org_id=org_id,
            orgc_id=org_id,
            info="test event",
            date="2024-02-13",
            analysis="test analysis",
            event_creator_email="test@mail.de",
        )

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = add_event_body.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/events/unpublish/{event_id}", headers=headers)

        assert response.status_code == 200
        response_json = response.json()

        assert response_json["saved"] is True
        assert response_json["success"] is True
        assert response_json["name"] == "Event unpublished."
        assert response_json["message"] == "Event unpublished."
        assert response_json["url"] == f"/events/unpublish/{event_id}"
        assert response_json["id"] == str(event_id)

    def test_publish_invalid_event(self: "TestUnpublishEvent", invalid_ids: str) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/events/unpublish/{invalid_ids}", headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["name"] == "Invalid event."
        assert response_json["message"] == "Invalid event."
        assert response_json["url"] == f"/events/unpublish/{invalid_ids}"

    def test_publish_event_response_format(self: "TestUnpublishEvent") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events/unpublish/1", headers=headers)

        assert response.headers["Content-Type"] == "application/json"

    def test_publish_event_authorization(self: "TestUnpublishEvent") -> None:
        headers = {"authorization": ""}
        response = client.post("/events/publish/1", headers=headers)

        assert response.status_code == 401


class TestAddTagToEvent:
    def test_add_existing_tag_to_attribute(
        self: "TestAddTagToEvent", db: Session, valid_local_add_tag_to_event: int
    ) -> None:
        add_org_body = Organisation(name="test", local=True)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_event_body = Event(
            org_id=org_id,
            orgc_id=org_id,
            info="test event",
            date="2024-02-13",
            analysis="test analysis",
            event_creator_email="test@mail.de",
        )

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = add_event_body.id

        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(400001, 500000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            inherited=False,
            is_galaxy=False,
            is_custom_galaxy=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_id = add_tag_body.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            f"/events/addTag/{event_id}/{tag_id}/local:{valid_local_add_tag_to_event}",
            headers=headers,
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["saved"] is True
        assert response_json["success"] == "Tag added"
        assert response_json["check_publish"] is True

    def test_add_invalid_or_non_existing_tag_to_attribute(
        self: "TestAddTagToEvent",
        db: Session,
        invalid_ids: str,
        valid_local_add_tag_to_event: int,
    ) -> None:
        add_org_body = Organisation(name="test", local=True)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_event_body = Event(
            org_id=org_id,
            orgc_id=org_id,
            info="test event",
            date="2024-02-13",
            analysis="test analysis",
            event_creator_email="test@mail.de",
        )

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = add_event_body.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            f"/events/addTag/{event_id}/{invalid_ids}/local:{valid_local_add_tag_to_event}",
            headers=headers,
        )
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["saved"] is False

    def test_add_tag_to_attribute_response_format(self: "TestAddTagToEvent", valid_local_add_tag_to_event: int) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            f"/events/addTag/1/1/local:{valid_local_add_tag_to_event}",
            headers=headers,
        )
        assert response.headers["Content-Type"] == "application/json"

    def test_add_tag_to_attribute_authorization(self: "TestAddTagToEvent", valid_local_add_tag_to_event: int) -> None:
        headers = {"authorization": ""}
        response = client.post(
            f"/events/addTag/1/1/local:{valid_local_add_tag_to_event}",
            headers=headers,
        )
        assert response.status_code == 401


class TestRemoveTagFromEvent:
    def test_remove_existing_tag_from_attribute(self: "TestRemoveTagFromEvent", db: Session) -> None:
        add_org_body = Organisation(name="test", local=True)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_event_body = Event(
            org_id=org_id,
            orgc_id=org_id,
            info="test event",
            date="2024-02-13",
            analysis="test analysis",
            event_creator_email="test@mail.de",
        )

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = add_event_body.id

        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(500001, 600000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            inherited=False,
            is_galaxy=False,
            is_custom_galaxy=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_id = add_tag_body.id

        add_event_tag_body = EventTag(event_id=event_id, tag_id=tag_id, local=False)

        db.add(add_event_tag_body)
        db.commit()
        db.refresh(add_event_tag_body)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/events/removeTag/{event_id}/{tag_id}", headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["saved"] is True
        assert response_json["success"] == "Tag removed"

    def test_remove_tag_from_attribute_response_format(self: "TestRemoveTagFromEvent") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events/removeTag/1/1", headers=headers)
        assert response.headers["Content-Type"] == "application/json"

    def test_remove_tag_from_attribute_authorization(self: "TestRemoveTagFromEvent") -> None:
        headers = {"authorization": ""}
        response = client.post("/events/removeTag/1/1", headers=headers)
        assert response.status_code == 401


# class TestAddAttributeViaFreeTextImport:
#     def test_add_attribute_via_free_text_import_valid_data(
#             self: "TestAddAttributeViaFreeTextImport",
#             db: Session,
#             add_attribute_via_free_text_import_valid_data: Dict[str, Any],
#     ) -> None:
#         add_org_body = Organisation(name="test", local=True)
#
#         db.add(add_org_body)
#         db.commit()
#         db.refresh(add_org_body)
#
#         org_id = add_org_body.id
#
#         add_event_body = Event(
#             org_id=org_id,
#             orgc_id=org_id,
#             info="test event",
#             date="2024-02-13",
#             analysis="test analysis",
#             event_creator_email="test@mail.de",
#         )
#
#         db.add(add_event_body)
#         db.commit()
#         db.refresh(add_event_body)
#
#         event_id = add_event_body.id
#
#         headers = {"authorization": environment.site_admin_user_token}
#         response = client.post(
#             f"/events/freeTextImport/{event_id}", json=add_attribute_via_free_text_import_valid_data, headers=headers
#         )
#
#         print(response.json())
#
#         assert response.status_code == 501
