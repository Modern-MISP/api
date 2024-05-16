from typing import Any

import pytest
import sqlalchemy as sa
from icecream import ic
from sqlalchemy.orm import Session

from mmisp.db.models.attribute import Attribute
from tests.environment import client
from tests.generators.sighting_generator import (
    generate_valid_random_sighting_data,
    generate_valid_random_sighting_with_filter_data,
)


@pytest.fixture(autouse=True)
def check_counts_stay_constant(db):
    count_attributes = db.execute("SELECT COUNT(*) FROM attributes").first()[0]
    count_events = db.execute("SELECT COUNT(*) FROM events").first()[0]
    count_sightings = db.execute("SELECT COUNT(*) FROM sightings").first()[0]
    yield
    ncount_attributes = db.execute("SELECT COUNT(*) FROM attributes").first()[0]
    ncount_events = db.execute("SELECT COUNT(*) FROM events").first()[0]
    ncount_sightings = db.execute("SELECT COUNT(*) FROM sightings").first()[0]

    assert count_attributes == ncount_attributes
    assert count_events == ncount_events
    assert count_sightings == ncount_sightings


@pytest.fixture(
    params=[
        generate_valid_random_sighting_data().dict(),
        generate_valid_random_sighting_data().dict(),
        generate_valid_random_sighting_data().dict(),
        generate_valid_random_sighting_with_filter_data().dict(),
        generate_valid_random_sighting_with_filter_data().dict(),
    ]
)
def sighting_data(request: Any) -> dict[str, Any]:
    return request.param


def delete_sighting(db, sighting_id):
    stmt = sa.sql.text("DELETE FROM sightings WHERE id=:id")
    db.execute(stmt, {"id": sighting_id})
    db.commit()


@pytest.fixture
def attributes_sighting_data(db, sighting_data, sharing_group, event):
    attributes = []
    for val in sighting_data["values"]:
        attribute = Attribute(
            event_id=event.id,
            category="other",
            type="text",
            value1=val,
            value2="",
            sharing_group_id=sharing_group.id,
        )

        db.add(attribute)
        db.commit()
        attributes.append(attribute)
        ic(attribute.asdict())

    yield attributes

    for a in attributes:
        db.delete(a)
    db.commit()


@pytest.fixture
def first_attribute_sighting_data(db, sighting_data, sharing_group, event):
    attribute = Attribute(
        event_id=event.id,
        category="other",
        type="text",
        value1=sighting_data["values"][0],
        value2="",
        sharing_group_id=sharing_group.id,
    )

    db.add(attribute)
    db.commit()
    ic(attribute.asdict())

    yield attribute

    db.delete(attribute)
    db.commit()


def test_add_sighting(
    attributes_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token
) -> None:
    attributes = attributes_sighting_data
    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = sighting_data["values"][-1]

    headers = {"authorization": site_admin_user_token}
    response = client.post("/sightings", json=sighting_data, headers=headers)
    response_data = response.json()
    ic(response_data)
    response_attribute_ids = [x["attribute_id"] for x in response_data]

    assert response.status_code == 201
    if sighting_data["filters"]:
        assert str(attributes[-1].id) in response_attribute_ids
        assert len(response_attribute_ids) == 1
    else:
        for a in attributes:
            assert str(a.id) in response_attribute_ids

    for sighting in response_data:
        delete_sighting(db, sighting["id"])


def test_add_sighting_with_invalid_data(
    attributes_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token
) -> None:
    attributes = attributes_sighting_data
    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = attributes[-1].value1

    headers = {"authorization": site_admin_user_token}
    response_first = client.post("/sightings", json=sighting_data, headers=headers)
    assert response_first.status_code == 201
    response_second = client.post("/sightings", json=sighting_data, headers=headers)
    assert response_second.status_code == 201
    response_third = client.post("/sightings", json=sighting_data, headers=headers)
    assert response_third.status_code == 201

    for sighting in response_first.json():
        delete_sighting(db, sighting["id"])
    for sighting in response_second.json():
        delete_sighting(db, sighting["id"])
    for sighting in response_third.json():
        delete_sighting(db, sighting["id"])


def test_add_sighting_missing_required_fields(
    attributes_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token
) -> None:
    attributes = attributes_sighting_data
    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = attributes[-1].value1

    incomplete_data = generate_valid_random_sighting_data().dict()
    del incomplete_data["values"]
    headers = {"authorization": site_admin_user_token}
    response = client.post("/sightings", json=incomplete_data, headers=headers)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "field required"


def test_add_sightings_at_index_success(
    first_attribute_sighting_data,
    sighting_data: dict[str, Any],
    db: Session,
    sharing_group,
    event,
    site_admin_user_token,
) -> None:
    attribute = first_attribute_sighting_data
    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = attribute.value1

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/sightings/{attribute.id}", headers=headers)
    assert response.status_code == 201
    response_data = response.json()
    assert "id" in response_data
    assert "event_id" in response_data
    assert "attribute_id" in response_data

    delete_sighting(db, response_data["id"])


def test_add_sighting_at_index_invalid_attribute(
    first_attribute_sighting_data,
    sighting_data: dict[str, Any],
    db: Session,
    sharing_group,
    event,
    site_admin_user_token,
) -> None:
    attribute = first_attribute_sighting_data

    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = attribute.value1

    non_existent_attribute_id = "0"
    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/sightings/{non_existent_attribute_id}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Attribute not found."


def test_get_sighting_success(
    first_attribute_sighting_data, sighting_data: dict[str, Any], db: Session, event, site_admin_user_token
) -> None:
    attribute = first_attribute_sighting_data

    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = attribute.value1

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/sightings/{event.id}", headers=headers)
    assert response.status_code == 200


def test_delete_sighting_success(
    first_attribute_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token
) -> None:
    attribute = first_attribute_sighting_data
    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = attribute.value1

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/sightings/{attribute.id}", headers=headers)
    assert response.status_code == 201

    sighting_id = response.json()["id"]

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/sightings/{sighting_id}", headers=headers)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["saved"]
    assert response_data["success"]
    assert response_data["message"] == "Sighting successfully deleted."
    assert response_data["name"] == "Sighting successfully deleted."


def test_delete_sighting_invalid_id(
    first_attribute_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token
) -> None:
    attribute = first_attribute_sighting_data
    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = attribute.value1

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/sightings/{attribute.id}", headers=headers)
    assert response.status_code == 201

    real_sighting_id = response.json()["id"]
    sighting_id = "0"

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/sightings/{sighting_id}", headers=headers)
    response_data = response.json()
    assert response.status_code == 404
    assert "detail" in response_data
    assert response_data["detail"] == "Sighting not found."

    delete_sighting(db, real_sighting_id)


def test_get_all_sightings_success(
    first_attribute_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token
) -> None:
    attribute = first_attribute_sighting_data
    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = attribute.value1

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/sightings/{attribute.id}", headers=headers)
    real_sighting_id = response.json()["id"]
    assert response.status_code == 201

    response = client.get("/sightings", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json()["sightings"], list)
    delete_sighting(db, real_sighting_id)


def test_get_sightings_response_format(
    first_attribute_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token
) -> None:
    attribute = first_attribute_sighting_data
    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = attribute.value1

    headers = {"authorization": site_admin_user_token}
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
        assert "Organisation" in sighting_wrapper

    ic(response_data)
    for x in response_data["sightings"]:
        delete_sighting(db, x["id"])
