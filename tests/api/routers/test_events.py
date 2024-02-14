from typing import Any, Dict

import pytest
from sqlalchemy.orm import Session

from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.organisation import Organisation

from ...environment import client, environment, get_db
from ...generators.event_generator import (
    generate_invalid_add_event_body,
    generate_invalid_id,
    generate_non_existing_id,
    generate_valid_add_event_body,
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

        response = client.get(f"/events/{event_id}")

        assert response.status_code == 501
        response_json = response.json()
        assert response_json["Event"]["id"] == str(event_id)
        assert response_json["Event"]["org_id"] == str(org_id)
        assert response_json["Event"]["orgc_id"] == str(org_id)
        assert response_json["Event"]["attribute_count"] == "1"
        assert response_json["Event"]["Attribute"][0]["id"] == str(attribute_id)

    def test_get_non_existing_event(self: "TestGetEventDetails", db: Session, invalid_ids: str) -> None:
        response = response = client.get(f"/events/{invalid_ids}")
        assert response.status_code == 404
