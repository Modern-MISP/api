from typing import Any, Dict

import pytest
from sqlalchemy.orm import Session

from ...environment import client, environment, get_db
from ...generators.event_generator import generate_invalid_add_event_body, generate_valid_add_event_body


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


class TestAddEvent:
    def test_add_event_valid_data(self: "TestAddEvent", add_event_valid_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/events", json=add_event_valid_data, headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["Event"]["info"] == add_event_valid_data["info"]
        assert response_json["Event"]["date"] == "2024-02-13"

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
