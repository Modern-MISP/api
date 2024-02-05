from typing import Any, Dict

import pytest
from sqlalchemy.orm import Session

from mmisp.db.models.event import Event
from mmisp.db.models.object import ObjectTemplate

from ...environment import client, environment, get_db
from ...generators.object_generator import (
    generate_random_search_query,
    generate_search_query,
    generate_specific_search_query,
    generate_valid_object_data,
    generate_valid_random_object_data,
)


@pytest.fixture(scope="function")
def db() -> Session:
    db_session = get_db()

    yield db_session

    db_session.close()


@pytest.fixture(
    params=[
        generate_valid_object_data().dict(),
        generate_valid_random_object_data().dict(),
        generate_valid_random_object_data().dict(),
        generate_valid_random_object_data().dict(),
        generate_valid_random_object_data().dict(),
    ]
)
def object_data(request: Any) -> Dict[str, Any]:
    return request.param


# --- Test cases ---


# Test add an object
def test_add_object_to_event(db: Session, object_data: Dict[str, Any]) -> None:
    object_template = ObjectTemplate(
        name="test_template", version="0.0.000", description="This is a test-template", meta_category="test"
    )
    db.add(object_template)

    db.commit()

    db.refresh(object_template)

    add_event_body = Event(
        info="test",
    )
    db.add(add_event_body)
    db.commit()

    db.refresh(add_event_body)

    object_template_id = object_template.id
    event_id = add_event_body.id

    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 200

    response_data = response.json()
    assert "object" in response_data
    assert int(response_data["object"]["event_id"]) == event_id


def test_add_object_response_format(db: Session, object_data: Dict[str, Any]) -> None:
    object_template = ObjectTemplate(
        name="test_template", version="0.0.000", description="This is a test-template", meta_category="test"
    )
    db.add(object_template)

    db.commit()

    db.refresh(object_template)

    add_event_body = Event(
        info="test",
    )
    db.add(add_event_body)
    db.commit()

    db.refresh(add_event_body)

    object_template_id = object_template.id
    event_id = add_event_body.id

    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    assert "object" in response.json()


def test_add_object_to_event_authorization(object_data: Dict[str, Any]) -> None:
    headers = {"authorization": ""}
    response = client.post("/feeds/", json=object_data, headers=headers)
    assert response.status_code == 401


# Test search an object
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
def search_data(request: Any) -> Dict[str, Any]:
    return request.param


def test_search_objects_with_filters(search_data: Dict[str, Any]) -> None:
    response = client.post("/objects/restsearch", json=search_data)
    assert response.status_code == 200

    response_data = response.json()
    assert "response" in response_data


def test_search_objects_response_format(search_data: Dict[str, Any]) -> None:
    response = client.post("/objects/restsearch", json=search_data)
    assert response.headers["Content-Type"] == "application/json"
    response_data = response.json()
    assert "response" in response_data

    assert isinstance(response_data["response"], list)


def test_search_objects_data_integrity(search_data: Dict[str, Any]) -> None:
    response = client.post("/objects/restsearch", json=search_data)
    response_data = response.json()
    for obj in response_data["response"]:
        assert "id" in obj["object"] != ""
        assert "name" in obj["object"] != ""
        assert "meta_category" in obj["object"] != ""
        assert "distribution" in obj["object"] != ""


# Test get object details
def test_get_object_details_valid_id(db: Session, object_data: Dict[str, Any]) -> None:
    object_template = ObjectTemplate(
        name="test_template", version="0.0.000", description="This is a test-template", meta_category="test"
    )
    db.add(object_template)

    db.commit()

    db.refresh(object_template)

    add_event_body = Event(
        info="test",
    )
    db.add(add_event_body)
    db.commit()

    db.refresh(add_event_body)

    object_template_id = object_template.id
    event_id = add_event_body.id

    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 200

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


def test_get_object_details_response_format(db: Session, object_data: Dict[str, Any]) -> None:
    object_template = ObjectTemplate(
        name="test_template", version="0.0.000", description="This is a test-template", meta_category="test"
    )
    db.add(object_template)

    db.commit()

    db.refresh(object_template)

    add_event_body = Event(
        info="test",
    )
    db.add(add_event_body)
    db.commit()

    db.refresh(add_event_body)

    object_template_id = object_template.id
    event_id = add_event_body.id

    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 200

    response_data = response.json()
    object_id = response_data["object"]["id"]

    response = client.get(f"/objects/{object_id}", headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    response_data = response.json()
    assert "object" in response_data


def test_get_object_details_invalid_id() -> None:
    object_id: str = "invalid_id"
    headers = {"authorization": environment.site_admin_user_token}
    response = client.get(f"/objects/{object_id}", headers=headers)
    assert response.status_code == 404


def test_get_object_details_data_integrity(db: Session, object_data: Dict[str, Any]) -> None:
    object_template = ObjectTemplate(
        name="test_template", version="0.0.000", description="This is a test-template", meta_category="test"
    )
    db.add(object_template)

    db.commit()

    db.refresh(object_template)

    add_event_body = Event(
        info="test",
    )
    db.add(add_event_body)
    db.commit()

    db.refresh(add_event_body)

    object_template_id = object_template.id
    event_id = add_event_body.id

    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 200

    response_data = response.json()
    object_id = response_data["object"]["id"]

    response = client.get(f"/objects/{object_id}", headers=headers)
    response_data = response.json()
    object_data = response_data["object"]
    assert isinstance(object_data["id"], str)
    assert isinstance(object_data["name"], str)


# Test delete object with hard delete
def test_delete_object_hard_delete(db: Session, object_data: Dict[str, Any]) -> None:
    object_template = ObjectTemplate(
        name="test_template", version="0.0.000", description="This is a test-template", meta_category="test"
    )
    db.add(object_template)

    db.commit()

    db.refresh(object_template)

    add_event_body = Event(
        info="test",
    )
    db.add(add_event_body)
    db.commit()

    db.refresh(add_event_body)

    object_template_id = object_template.id
    event_id = add_event_body.id

    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 200

    response_data = response.json()
    object_id = response_data["object"]["id"]

    response = client.delete(f"/objects/{object_id}/true", headers=headers)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["success"] is True
    assert response_data["saved"] is True
    assert response_data["message"] == "Object has been permanently deleted."


# Test delete object with soft delete
def test_delete_object_soft_delete(db: Session, object_data: Dict[str, Any]) -> None:
    object_template = ObjectTemplate(
        name="test_template", version="0.0.000", description="This is a test-template", meta_category="test"
    )
    db.add(object_template)

    db.commit()

    db.refresh(object_template)

    add_event_body = Event(
        info="test",
    )
    db.add(add_event_body)
    db.commit()

    db.refresh(add_event_body)

    object_template_id = object_template.id
    event_id = add_event_body.id

    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 200

    response_data = response.json()
    object_id = response_data["object"]["id"]

    response_delete = client.delete(f"/objects/{object_id}/false", headers=headers)
    assert response_delete.status_code == 200

    response_data = response_delete.json()
    assert response_data["saved"] is True
    assert response_data["success"] is True
    assert response_data["message"] == "Object has been soft deleted."


def test_delete_object_invalid_id() -> None:
    object_id = "invalid_id"
    headers = {"authorization": environment.site_admin_user_token}
    response_delete = client.delete(f"/objects/{object_id}/true", headers=headers)
    assert response_delete.status_code == 404
    assert "detail" in response_delete.json()


def test_delete_object_invalid_hard_delete(db: Session, object_data: Dict[str, Any]) -> None:
    object_template = ObjectTemplate(
        name="test_template", version="0.0.000", description="This is a test-template", meta_category="test"
    )
    db.add(object_template)

    db.commit()

    db.refresh(object_template)

    add_event_body = Event(
        info="test",
    )
    db.add(add_event_body)
    db.commit()

    db.refresh(add_event_body)

    object_template_id = object_template.id
    event_id = add_event_body.id

    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 200

    response_data = response.json()
    object_id = response_data["object"]["id"]

    response_delete = client.delete(f"/objects/{object_id}/invalid_value", headers=headers)
    assert response_delete.status_code == 400
    assert "detail" in response_delete.json()


def test_delete_object_no_authorization(db: Session, object_data: Dict[str, Any]) -> None:
    object_template = ObjectTemplate(
        name="test_template", version="0.0.000", description="This is a test-template", meta_category="test"
    )
    db.add(object_template)

    db.commit()

    db.refresh(object_template)

    add_event_body = Event(
        info="test",
    )
    db.add(add_event_body)
    db.commit()

    db.refresh(add_event_body)

    object_template_id = object_template.id
    event_id = add_event_body.id

    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 200

    response_data = response.json()
    object_id = response_data["object"]["id"]

    response_delete = client.delete(f"/objects/{object_id}/true")
    assert response_delete.status_code == 401
    assert "detail" in response_delete.json()
