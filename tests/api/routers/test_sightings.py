from typing import Any

import pytest
import pytest_asyncio
import sqlalchemy as sa
from icecream import ic
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from mmisp.db.models.attribute import Attribute
from mmisp.tests.generators.sighting_generator import (
    generate_valid_random_sighting_data,
    generate_valid_random_sighting_with_filter_data,
)


@pytest_asyncio.fixture(autouse=True)
async def check_counts_stay_constant(db):
    count_attributes = (await db.execute(text("SELECT COUNT(*) FROM attributes"))).first()[0]
    count_events = (await db.execute(text("SELECT COUNT(*) FROM events"))).first()[0]
    count_sightings = (await db.execute(text("SELECT COUNT(*) FROM sightings"))).first()[0]
    yield
    ncount_attributes = (await db.execute(text("SELECT COUNT(*) FROM attributes"))).first()[0]
    ncount_events = (await db.execute(text("SELECT COUNT(*) FROM events"))).first()[0]
    ncount_sightings = (await db.execute(text("SELECT COUNT(*) FROM sightings"))).first()[0]

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


async def delete_sighting(db, sighting_id):
    stmt = sa.sql.text("DELETE FROM sightings WHERE id=:id")
    await db.execute(stmt, {"id": sighting_id})
    await db.commit()


@pytest_asyncio.fixture
async def attributes_sighting_data(db, sighting_data, sharing_group, event):
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
        await db.commit()
        attributes.append(attribute)
        ic(attribute.asdict())

    yield attributes

    for a in attributes:
        await db.delete(a)
    await db.commit()


@pytest_asyncio.fixture
async def first_attribute_sighting_data(db, sighting_data, sharing_group, event):
    attribute = Attribute(
        event_id=event.id,
        category="other",
        type="text",
        value1=sighting_data["values"][0],
        value2="",
        sharing_group_id=sharing_group.id,
    )

    db.add(attribute)
    await db.commit()
    ic(attribute.asdict())

    yield attribute

    await db.delete(attribute)
    await db.commit()


@pytest.mark.asyncio
async def test_add_sighting(
    attributes_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token, client
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
        assert attributes[-1].id in response_attribute_ids
        assert len(response_attribute_ids) == 1
    else:
        for a in attributes:
            assert a.id in response_attribute_ids

    for sighting in response_data:
        await delete_sighting(db, sighting["id"])


@pytest.mark.asyncio
async def test_add_sighting_with_invalid_data(
    attributes_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token, client
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
        await delete_sighting(db, sighting["id"])
    for sighting in response_second.json():
        await delete_sighting(db, sighting["id"])
    for sighting in response_third.json():
        await delete_sighting(db, sighting["id"])


@pytest.mark.asyncio
async def test_add_sighting_missing_required_fields(
    attributes_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token, client
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


@pytest.mark.asyncio
async def test_add_sightings_at_index_success(
    first_attribute_sighting_data,
    sighting_data: dict[str, Any],
    db: Session,
    sharing_group,
    event,
    site_admin_user_token,
    client,
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

    await delete_sighting(db, response_data["id"])

@pytest.mark.asyncio
async def test_add_sightings_at_uuid_index_success(
    first_attribute_sighting_data,
    sighting_data: dict[str, Any],
    db: Session,
    sharing_group,
    event,
    site_admin_user_token,
    client,
) -> None:
    attribute = first_attribute_sighting_data
    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = attribute.value1

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/sightings/{attribute.uuid}", headers=headers)
    assert response.status_code == 201
    response_data = response.json()
    assert "id" in response_data
    assert "event_id" in response_data
    assert "attribute_id" in response_data

    await delete_sighting(db, response_data["id"])


@pytest.mark.asyncio
async def test_add_sighting_at_index_invalid_attribute(
    first_attribute_sighting_data,
    sighting_data: dict[str, Any],
    db: Session,
    sharing_group,
    event,
    site_admin_user_token,
    client,
) -> None:
    attribute = first_attribute_sighting_data

    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = attribute.value1

    non_existent_attribute_id = "0"
    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/sightings/{non_existent_attribute_id}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Attribute not found."

    unused_uuid = "a469325efe2f4f32a6854579f415ec6a"  #Just a random UUID -> mostlikely unused
    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/sightings/{unused_uuid}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Attribute not found."




@pytest.mark.asyncio
async def test_get_sighting_success(
    first_attribute_sighting_data, sighting_data: dict[str, Any], db: Session, event, site_admin_user_token, client
) -> None:
    attribute = first_attribute_sighting_data

    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = attribute.value1

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/sightings/{event.id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_sighting_by_uuid_success(
    first_attribute_sighting_data, sighting_data: dict[str, Any], db: Session, event, site_admin_user_token, client
) -> None:
    attribute = first_attribute_sighting_data

    if sighting_data["filters"]:
        sighting_data["filters"]["value1"] = attribute.value1

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/sightings/{event.uuid}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_sighting_success(
    first_attribute_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token, client
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


@pytest.mark.asyncio
async def test_delete_sighting_invalid_id(
    first_attribute_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token, client
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

    await delete_sighting(db, real_sighting_id)


@pytest.mark.asyncio
async def test_get_all_sightings_success(
    first_attribute_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token, client
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
    await delete_sighting(db, real_sighting_id
    )


@pytest.mark.asyncio
async def test_get_sightings_response_format(
    first_attribute_sighting_data, sighting_data: dict[str, Any], db: Session, site_admin_user_token, client
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
        await delete_sighting(db, x["id"])
