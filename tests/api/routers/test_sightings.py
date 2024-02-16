import time
from datetime import datetime
from typing import Any

import pytest

from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.organisation import Organisation
from tests.environment import client, environment, get_db
from tests.generators.sighting_generator import (
    generate_valid_random_sighting_data,
)


@pytest.fixture(
    params=[
        generate_valid_random_sighting_data().dict(),
        generate_valid_random_sighting_data().dict(),
        generate_valid_random_sighting_data().dict(),
        generate_valid_random_sighting_data().dict(),
        generate_valid_random_sighting_data().dict(),
    ]
)
def sighting_data(request: Any) -> dict[str, Any]:
    return request.param


class TestAddSighting:
    def test_add_sighting(self: "TestAddSighting", sighting_data: dict[str, Any]) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
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

        for val in sighting_data["values"]:
            attributes = Attribute(
                event_id=event.id,
                category="test",
                type="test",
                value=val,
            )

            db.add(attributes)

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/sightings", json=sighting_data, headers=headers)
        assert response.status_code == 201
        assert "sightings" in response.json()

    def test_add_sighting_with_invalid_data(self: "TestAddSighting", sighting_data: dict[str, Any]) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
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

        for val in sighting_data["values"]:
            attributes = Attribute(
                event_id=event.id,
                category="test",
                type="test",
                value=val,
            )

            db.add(attributes)

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response_first = client.post("/sightings", json=sighting_data, headers=headers)
        assert response_first.status_code == 201
        response_second = client.post("/sightings", json=sighting_data, headers=headers)
        assert response_second.status_code == 201
        response_second = client.post("/sightings", json=sighting_data, headers=headers)
        assert response_second.status_code == 201

    def test_add_sighting_missing_required_fields(self: "TestAddSighting", sighting_data: dict[str, Any]) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
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

        for val in sighting_data["values"]:
            attributes = Attribute(
                event_id=event.id,
                category="test",
                type="test",
                value=val,
            )

            db.add(attributes)

        db.commit()

        incomplete_data = generate_valid_random_sighting_data().dict()
        del incomplete_data["values"]
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/sightings", json=incomplete_data, headers=headers)
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "field required"

    def test_add_sighting_unauthorized(self: "TestAddSighting", sighting_data: dict[str, Any]) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
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

        for val in sighting_data["values"]:
            attributes = Attribute(
                event_id=event.id,
                category="test",
                type="test",
                value=val,
            )

            db.add(attributes)

        db.commit()

        headers = {"authorization": ""}
        response = client.post("/sightings", json=sighting_data, headers=headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"


class TestAddSightingAtIndex:
    def test_add_sightings_at_index_success(self: "TestAddSightingAtIndex", sighting_data: dict[str, Any]) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
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

        attribute = Attribute(
            event_id=event.id,
            category="test",
            type="test",
            value=sighting_data["values"][0],
        )

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/sightings/{attribute.id}", headers=headers)
        assert response.status_code == 201
        assert "sighting" in response.json()
        assert "id" in response.json()["sighting"]
        assert "event_id" in response.json()["sighting"]
        assert "attribute_id" in response.json()["sighting"]

    def test_add_sighting_at_index_invalid_attribute(
        self: "TestAddSightingAtIndex", sighting_data: dict[str, Any]
    ) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
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

        non_existent_attribute_id = "0"
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/sightings/{non_existent_attribute_id}", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Attribute not found."

    def test_add_sightings_at_index_unauthorized(self: "TestAddSightingAtIndex", sighting_data: dict[str, Any]) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
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

        attribute = Attribute(
            event_id=event.id,
            category="test",
            type="test",
            value=sighting_data["values"][0],
        )

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        headers = {"authorization": ""}
        response = client.post(f"/sightings/{attribute.id}", headers=headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"


class TestGetSighting:
    def test_get_sighting_success(self: "TestGetSighting", sighting_data: dict[str, Any]) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
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

        attribute = Attribute(
            event_id=event.id,
            category="test",
            type="test",
            value=sighting_data["values"][0],
        )

        db.add(attribute)
        db.commit()

        response = client.get(f"/sightings/{event.id}")
        assert response.status_code == 200
        assert "sightings" in response.json()


class TestDeleteSighting:
    def test_delete_sighting_success(self: "TestDeleteSighting", sighting_data: dict[str, Any]) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
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

        attribute = Attribute(
            event_id=event.id,
            category="test",
            type="test",
            value=sighting_data["values"][0],
        )

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/sightings/{attribute.id}", headers=headers)
        assert response.status_code == 201

        sighting_id = response.json()["sighting"]["id"]

        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/sightings/{sighting_id}", headers=headers)
        response_data = response.json()
        assert response.status_code == 200
        assert response_data["saved"] is True
        assert response_data["success"] is True
        assert response_data["message"] == "Sighting successfully deleted."
        assert response_data["name"] == "Sighting successfully deleted."

    def test_delete_sighting_invalid_id(self: "TestDeleteSighting", sighting_data: dict[str, Any]) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
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

        attribute = Attribute(
            event_id=event.id,
            category="test",
            type="test",
            value=sighting_data["values"][0],
        )

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/sightings/{attribute.id}", headers=headers)
        assert response.status_code == 201

        sighting_id = "0"

        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/sightings/{sighting_id}", headers=headers)
        assert response.status_code == 404
        assert "detail" in response.json()
        assert response.json()["detail"] == "Sighting not found."

    def test_delete_no_authorization(self: "TestDeleteSighting", sighting_data: dict[str, Any]) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
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

        attribute = Attribute(
            event_id=event.id,
            category="test",
            type="test",
            value=sighting_data["values"][0],
        )

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/sightings/{attribute.id}", headers=headers)
        assert response.status_code == 201

        sighting_id = response.json()["sighting"]["id"]

        headers = {"authorization": ""}
        response = client.delete(f"/sightings/{sighting_id}", headers=headers)
        assert response.status_code == 401
        assert "detail" in response.json()
        assert response.json()["detail"] == "Unauthorized"


class TestGetAllSightings:
    def test_get_all_sightings_success(self: "TestGetAllSightings", sighting_data: dict[str, Any]) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
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

        attribute = Attribute(
            event_id=event.id,
            category="test",
            type="test",
            value=sighting_data["values"][0],
        )

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/sightings/{attribute.id}", headers=headers)
        assert response.status_code == 201

        response = client.get("/sightings")
        assert response.status_code == 200
        assert isinstance(response.json()["sightings"], list)

    def test_get_sightings_response_format(self: "TestGetAllSightings", sighting_data: dict[str, Any]) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=datetime.utcnow(),
            date_modified=datetime.utcnow(),
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

        attribute = Attribute(
            event_id=event.id,
            category="test",
            type="test",
            value=sighting_data["values"][0],
        )

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/sightings/{attribute.id}", headers=headers)
        assert response.status_code == 201

        response = client.get("/sightings")
        assert response.headers["Content-Type"] == "application/json"
        response_data = response.json()
        assert isinstance(response_data["sightings"], list)

        # Test all required fields
        assert "sightings" in response_data
        for sighting_wrapper in response_data["sightings"]:
            assert "id" in sighting_wrapper
            assert "uuid" in sighting_wrapper
            assert "attribute_id" in sighting_wrapper
            assert "event_id" in sighting_wrapper
            assert "org_id" in sighting_wrapper
            assert "date_sighting" in sighting_wrapper
            assert "organisation" in sighting_wrapper
