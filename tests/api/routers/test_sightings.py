from datetime import datetime
from time import time
from typing import Any
from uuid import uuid4

import pytest

from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from tests.database import get_db
from tests.environment import client, environment
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
    @staticmethod
    def test_add_sighting(sighting_data: dict[str, Any]) -> None:
        db = get_db()

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
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

    @staticmethod
    def test_add_sighting_with_invalid_data(sighting_data: dict[str, Any]) -> None:
        db = get_db()

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
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

    @staticmethod
    def test_add_sighting_missing_required_fields(sighting_data: dict[str, Any]) -> None:
        db = get_db()

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
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


class TestAddSightingAtIndex:
    @staticmethod
    def test_add_sightings_at_index_success(sighting_data: dict[str, Any]) -> None:
        db = get_db()

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
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
        assert "sightings" in response.json()
        assert "id" in response.json()["sightings"][0]
        assert "event_id" in response.json()["sightings"][0]
        assert "attribute_id" in response.json()["sightings"][0]

    @staticmethod
    def test_add_sighting_at_index_invalid_attribute(sighting_data: dict[str, Any]) -> None:
        db = get_db()

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
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

        non_existent_attribute_id = "0"
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/sightings/{non_existent_attribute_id}", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Attribute not found."


class TestGetSighting:
    @staticmethod
    def test_get_sighting_success(sighting_data: dict[str, Any]) -> None:
        db = get_db()

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
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

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/sightings/{event.id}", headers=headers)
        assert response.status_code == 200
        assert "sightings" in response.json()


class TestDeleteSighting:
    @staticmethod
    def test_delete_sighting_success(sighting_data: dict[str, Any]) -> None:
        db = get_db()

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
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

        sighting_id = response.json()["sightings"][0]["id"]

        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/sightings/{sighting_id}", headers=headers)
        response_data = response.json()
        assert response.status_code == 200
        assert response_data["saved"] is True
        assert response_data["success"] is True
        assert response_data["message"] == "Sighting successfully deleted."
        assert response_data["name"] == "Sighting successfully deleted."

    @staticmethod
    def test_delete_sighting_invalid_id(sighting_data: dict[str, Any]) -> None:
        db = get_db()

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
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


class TestGetAllSightings:
    @staticmethod
    def test_get_all_sightings_success(sighting_data: dict[str, Any]) -> None:
        db = get_db()

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
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

        response = client.get("/sightings", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json()["sightings"], list)

    @staticmethod
    def test_get_sightings_response_format(sighting_data: dict[str, Any]) -> None:
        db = get_db()

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
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

        response = client.get("/sightings", headers=headers)
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


def generate_unique_email() -> str:
    timestamp = int(time())
    random_str = uuid4().hex
    email = f"unique-{timestamp}-{random_str}@test"
    return email
