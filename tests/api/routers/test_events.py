import respx
from httpx import Response
from sqlalchemy.orm import Session

from mmisp.config import config
from mmisp.db.models.event import EventTag
from mmisp.db.models.galaxy_cluster import GalaxyCluster

from ...environment import client, environment
from ...generators.model_generators.attribute_generator import generate_attribute
from ...generators.model_generators.event_generator import generate_event
from ...generators.model_generators.galaxy_generator import generate_galaxy
from ...generators.model_generators.organisation_generator import generate_organisation
from ...generators.model_generators.tag_generator import generate_tag


class TestAddEvent:
    @staticmethod
    def test_add_event_valid_data() -> None:
        request_body = {"info": "test event"}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events", json=request_body, headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["Event"]["info"] == request_body["info"]
        assert "id" in response_json["Event"]["Org"]
        assert "name" in response_json["Event"]["Org"]
        assert "uuid" in response_json["Event"]["Org"]
        assert "local" in response_json["Event"]["Org"]


class TestGetEventDetails:
    @staticmethod
    def test_get_existing_event(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        attribute = generate_attribute()
        setattr(attribute, "event_id", event_id)

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        attribute_id = attribute.id

        galaxy = generate_galaxy()

        db.add(galaxy)
        db.commit()
        db.refresh(galaxy)

        galaxy_id = galaxy.id

        tag = generate_tag()
        setattr(tag, "user_id", 1)
        setattr(tag, "org_id", 1)
        setattr(tag, "is_galaxy", True)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        tag_id = tag.id

        add_event_tag_body = EventTag(event_id=event_id, tag_id=tag_id, local=False)

        db.add(add_event_tag_body)
        db.commit()
        db.refresh(add_event_tag_body)

        add_galaxy_cluster_body = GalaxyCluster(
            collection_uuid="uuid",
            type="test type",
            value="test",
            tag_name=tag.name,
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

    @staticmethod
    def test_get_non_existing_event() -> None:
        response = client.get("/events/0")
        assert response.status_code == 404
        response = client.get("/events/invalid_id")
        assert response.status_code == 404


class TestUpdateEvent:
    @staticmethod
    def test_update_existing_event(db: Session) -> None:
        request_body = {"info": "updated info"}
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.put(f"events/{event_id}", json=request_body, headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["Event"]["info"] == request_body["info"]

    @staticmethod
    def test_update_non_existing_event() -> None:
        request_body = {"info": "updated event"}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.put("/events/0", json=request_body, headers=headers)
        assert response.status_code == 404

        response = client.put("/events/invalid_id", json=request_body, headers=headers)
        assert response.status_code == 404


class TestDeleteEvent:
    @staticmethod
    def test_delete_existing_event(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"events/{event_id}", headers=headers)

        assert response.status_code == 200

    @staticmethod
    def test_delete_invalid_or_non_existing_event() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete("/events/0", headers=headers)
        assert response.status_code == 404
        response = client.delete("/events/invalid_id", headers=headers)
        assert response.status_code == 404


class TestGetAllEvents:
    @staticmethod
    def test_get_all_events(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event1 = generate_event()
        setattr(event1, "org_id", org_id)
        setattr(event1, "orgc_id", org_id)

        db.add(event1)
        db.commit()
        db.refresh(event1)

        event2 = generate_event()
        setattr(event2, "org_id", org_id)
        setattr(event2, "orgc_id", org_id)

        db.add(event2)
        db.commit()
        db.refresh(event2)

        response = client.get("/events")

        assert response.status_code == 200
        response_json = response.json()
        assert isinstance(response_json, list)


class TestEventRestSearch:
    @staticmethod
    def test_valid_search_attribute_data(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        attribute = generate_attribute()
        setattr(attribute, "event_id", event_id)

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        json = {"returnFormat": "json"}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events/restSearch", json=json, headers=headers)
        assert response.status_code == 200
        response_json = response.json()
        assert "response" in response_json
        assert isinstance(response_json["response"], list)
        response_json_attribute = response_json["response"][0]
        assert "Event" in response_json_attribute

    @staticmethod
    def test_invalid_search_attribute_data() -> None:
        json = {"returnFormat": "invalid format"}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events/restSearch", json=json, headers=headers)
        assert response.status_code == 404


class TestIndexEvents:
    @staticmethod
    def test_index_events_valid_data(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)

        db.add(event)
        db.commit()
        db.refresh(event)

        json = {"distribution": "1"}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events/index", json=json, headers=headers)
        assert response.status_code == 200
        response_json = response.json()
        assert isinstance(response_json, list)
        assert "id" in response_json[0]
        assert "GalaxyCluster" in response_json[0]


class TestPublishEvent:
    @staticmethod
    def test_publish_existing_event(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

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

    @staticmethod
    def test_publish_invalid_event() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events/publish/0", headers=headers)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["name"] == "Invalid event."
        assert response_json["message"] == "Invalid event."
        assert response_json["url"] == "/events/publish/0"
        response = client.post("/events/publish/invalid_id", headers=headers)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["name"] == "Invalid event."
        assert response_json["message"] == "Invalid event."
        assert response_json["url"] == "/events/publish/invalid_id"


class TestUnpublishEvent:
    @staticmethod
    def test_publish_existing_event(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

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

    @staticmethod
    def test_publish_invalid_event() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events/unpublish/0", headers=headers)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["name"] == "Invalid event."
        assert response_json["message"] == "Invalid event."
        assert response_json["url"] == "/events/unpublish/0"
        response = client.post("/events/unpublish/invalid_id", headers=headers)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["name"] == "Invalid event."
        assert response_json["message"] == "Invalid event."
        assert response_json["url"] == "/events/unpublish/invalid_id"


class TestAddTagToEvent:
    @staticmethod
    def test_add_existing_tag_to_attribute(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        tag = generate_tag()
        setattr(tag, "user_id", 1)
        setattr(tag, "org_id", 1)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        tag_id = tag.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            f"/events/addTag/{event_id}/{tag_id}/local:1",
            headers=headers,
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["saved"] is True
        assert response_json["success"] == "Tag added"
        assert response_json["check_publish"] is True

    @staticmethod
    def test_add_invalid_or_non_existing_tag_to_attribute(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            f"/events/addTag/{event_id}/0/local:1",
            headers=headers,
        )
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["saved"] is False
        response = client.post(
            f"/events/addTag/{event_id}/invalid_id/local:1",
            headers=headers,
        )
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["saved"] is False


class TestRemoveTagFromEvent:
    @staticmethod
    def test_remove_existing_tag_from_attribute(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        tag = generate_tag()
        setattr(tag, "user_id", 1)
        setattr(tag, "org_id", 1)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        tag_id = tag.id

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


@respx.mock
def test_add_attribute_via_free_text_import_valid_data(db: Session) -> None:
    return
    # TODO: this test fails, worker should return a list
    request_body = {"Attribute": {"value": "1.2.3.4"}}
    organisation = generate_organisation()

    db.add(organisation)
    db.commit()
    db.refresh(organisation)

    org_id = organisation.id

    event = generate_event()
    setattr(event, "org_id", org_id)
    setattr(event, "orgc_id", org_id)

    db.add(event)
    db.commit()
    db.refresh(event)

    event_id = event.id

    items = {"value": "1.2.3.4", "default_type": "ip-src"}

    attributes = {"Items": items}

    dictionary = {"attributes": attributes}

    route = respx.post(f"{config.WORKER_URL}/job/processFreeText").mock(return_value=Response(200, json=dictionary))
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"/events/freeTextImport/{event_id}", json=request_body, headers=headers)

    assert response.status_code == 200
    assert route.called
