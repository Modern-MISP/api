from typing import Any, Dict

import pytest
from sqlalchemy.orm import Session

from mmisp.api_schemas.events.add_edit_get_event_response import AddEditGetEventDetails

from ...environment import client, environment, get_db
from ...generators.event_generator import generate_valid_add_event_body


@pytest.fixture(scope="function")
def db() -> Session:
    db_session = get_db()

    yield db_session

    db_session.close()


@pytest.fixture(scope="module")
def add_event_valid_data() -> Dict[str, Any]:
    return generate_valid_add_event_body().dict()


class TestAddEvent:
    def test_add_event_valid_data(self: "TestAddEvent", add_event_valid_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events", json=add_event_valid_data, headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        for attribute in AddEditGetEventDetails.__dict__.keys():
            assert attribute in response_json["Event"]

    def test_add_event_invalid_data(self: "TestAddEvent", add_event_invalid_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events", json=add_event_invalid_data, headers=headers)

        if not add_event_invalid_data["id"]:
            assert response.status_code == 400
        elif not isinstance(add_event_invalid_data["id"], str):
            assert response.status_code == 403

    def test_add_event_response_format(self: "TestAddEvent", add_event_valid_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events", json=add_event_valid_data, headers=headers)

        assert response.headers["Content-Type"] == "application/json"

    def test_add_event_authorization(self: "TestAddEvent", add_event_valid_data: Dict[str, Any]) -> None:
        headers = {"authorization": ""}
        response = client.post("/events", json=add_event_valid_data, headers=headers)

        assert response.status_code == 401
