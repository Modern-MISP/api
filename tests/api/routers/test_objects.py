from typing import Any

import pytest
import pytest_asyncio
import sqlalchemy as sa
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.db.models.object import ObjectTemplate
from mmisp.tests.generators.object_generator import (
    generate_random_search_query,
    generate_search_query,
    generate_specific_search_query,
    generate_valid_object_data,
    generate_valid_random_object_data,
)


@pytest_asyncio.fixture(autouse=True)
async def check_counts_stay_constant(db):
    count_sharing_groups = (await db.execute(sa.text("SELECT COUNT(*) FROM sharing_groups"))).first()[0]
    count_sharing_groups_orgs = (await db.execute(sa.text("SELECT COUNT(*) FROM sharing_group_orgs"))).first()[0]
    count_sharing_groups_servers = (await db.execute(sa.text("SELECT COUNT(*) FROM sharing_group_servers"))).first()[0]
    yield
    ncount_sharing_groups = (await db.execute(sa.text("SELECT COUNT(*) FROM sharing_groups"))).first()[0]
    ncount_sharing_groups_orgs = (await db.execute(sa.text("SELECT COUNT(*) FROM sharing_group_orgs"))).first()[0]
    ncount_sharing_groups_servers = (await db.execute(sa.text("SELECT COUNT(*) FROM sharing_group_servers"))).first()[0]

    assert count_sharing_groups == ncount_sharing_groups
    assert count_sharing_groups_orgs == ncount_sharing_groups_orgs
    assert count_sharing_groups_servers == ncount_sharing_groups_servers


@pytest.fixture(
    params=[
        generate_valid_object_data().dict(),
        generate_valid_random_object_data().dict(),
        generate_valid_random_object_data().dict(),
        generate_valid_random_object_data().dict(),
        generate_valid_random_object_data().dict(),
    ]
)
def object_data(request: Any) -> dict[str, Any]:
    return request.param


@pytest_asyncio.fixture
async def object_template(db, organisation, site_admin_user):
    object_template = ObjectTemplate(
        name="test_template", user_id=site_admin_user.id, org_id=organisation.id, version=100
    )
    db.add(object_template)
    await db.flush()
    await db.refresh(object_template)

    yield object_template

    await db.delete(object_template)


async def delete_attributes_from_object_resp(db, response_data):
    ic(response_data)
    attribute_ids = [x["id"] for x in response_data["Object"]["Attribute"]]
    stmt = sa.sql.text("DELETE FROM attributes WHERE id=:id")

    for aid in attribute_ids:
        await db.execute(stmt, {"id": aid})
    await db.commit()

    ic(response_data)
    stmt = sa.sql.text("DELETE FROM objects WHERE id=:id")
    await db.execute(stmt, {"id": response_data["Object"]["id"]})
    await db.commit()


@pytest.mark.asyncio
async def test_add_object_to_event(
    object_data: dict[str, Any], sharing_group, object_template, event, site_admin_user_token, db, client
) -> None:
    object_data["sharing_group_id"] = sharing_group.id
    if object_data["Attribute"]:
        for attribute in object_data["Attribute"]:
            attribute["sharing_group_id"] = sharing_group.id
    object_data["event_id"] = event.id

    object_template_id = object_template.id
    event_id = event.id
    ic(object_data)
    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 201

    response_data = response.json()
    assert "Object" in response_data
    assert int(response_data["Object"]["event_id"]) == event_id

    await delete_attributes_from_object_resp(db, response_data)


@pytest.mark.asyncio
async def test_add_object_response_format(
    object_data: dict[str, Any], db: AsyncSession, event, site_admin_user_token, object_template, sharing_group, client
) -> None:
    object_data["sharing_group_id"] = sharing_group.id
    if object_data["Attribute"]:
        for attribute in object_data["Attribute"]:
            attribute["sharing_group_id"] = sharing_group.id

    object_data["event_id"] = event.id
    object_template_id = object_template.id
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    assert "Object" in response.json()

    response_data = response.json()
    await delete_attributes_from_object_resp(db, response_data)


@pytest.fixture(
    params=[
        generate_specific_search_query().dict(),
        generate_search_query().dict(),
        generate_random_search_query().dict(),
        generate_random_search_query().dict(),
    ]
)
def search_data(request: Any) -> dict[str, Any]:
    return request.param


@pytest.mark.asyncio
async def test_search_objects_with_filters(search_data: dict[str, Any], site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/objects/restsearch", json=search_data, headers=headers)
    assert response.status_code == 200

    response_data = response.json()
    assert "response" in response_data
    assert isinstance(response_data["response"], list)
    for obj in response_data["response"]:
        assert "id" in obj["object"] != ""
        assert "name" in obj["object"] != ""
        assert "sharing_group_id" in obj["object"] != ""
        assert "distribution" in obj["object"] != ""
        assert "comment" in obj["object"] != ""


@pytest.mark.asyncio
async def test_search_objects_response_format(search_data: dict[str, Any], site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/objects/restsearch", json=search_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    response_data = response.json()
    assert "response" in response_data
    assert isinstance(response_data["response"], list)


@pytest.mark.asyncio
async def test_search_objects_data_integrity(search_data: dict[str, Any], site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/objects/restsearch", json=search_data, headers=headers)
    response_data = response.json()
    for obj in response_data["response"]:
        assert "id" in obj["object"] != ""
        assert "name" in obj["object"] != ""
        assert "meta_category" in obj["object"] != ""
        assert "distribution" in obj["object"] != ""


@pytest.mark.asyncio
async def test_get_object_details_valid_id(
    object_data: dict[str, Any], db: AsyncSession, sharing_group, object_template, event, site_admin_user_token, client
) -> None:
    object_data["sharing_group_id"] = sharing_group.id
    if object_data["Attribute"]:
        for attribute in object_data["Attribute"]:
            attribute["sharing_group_id"] = sharing_group.id

    object_data["event_id"] = event.id

    object_template_id = object_template.id
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 201

    response_data = response.json()
    object_id = response_data["Object"]["id"]
    response = client.get(f"/objects/{object_id}", headers=headers)
    assert response.status_code == 200

    response_data = response.json()
    assert "Object" in response_data
    object_data = response_data["Object"]
    assert object_data["id"] == object_id
    assert "name" in object_data
    assert "meta_category" in object_data
    assert "distribution" in object_data
    assert "comment" in object_data
    assert "sharing_group_id" in object_data

    await delete_attributes_from_object_resp(db, response.json())


@pytest.mark.asyncio
async def test_get_object_details_response_format(
    object_data: dict[str, Any],
    db: AsyncSession,
    instance_owner_org,
    object_template,
    event,
    site_admin_user_token,
    sharing_group,
    client,
) -> None:
    object_data["sharing_group_id"] = sharing_group.id
    if object_data["Attribute"]:
        for attribute in object_data["Attribute"]:
            attribute["sharing_group_id"] = sharing_group.id

    object_data["event_id"] = event.id

    await db.commit()

    object_template_id = object_template.id
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 201

    response_data = response.json()
    object_id = response_data["Object"]["id"]
    response = client.get(f"/objects/{object_id}", headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    response_data = response.json()
    assert "Object" in response_data
    await delete_attributes_from_object_resp(db, response_data)


@pytest.mark.asyncio
async def test_get_object_details_invalid_id(site_admin_user_token, client) -> None:
    object_id: str = "invalid_id"
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/objects/{object_id}", headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_object_details_data_integrity(
    object_data: dict[str, Any], db: AsyncSession, sharing_group, event, object_template, site_admin_user_token, client
) -> None:
    object_data["sharing_group_id"] = sharing_group.id
    if object_data["Attribute"]:
        for attribute in object_data["Attribute"]:
            attribute["sharing_group_id"] = sharing_group.id

    object_data["event_id"] = event.id
    await db.commit()

    object_template_id = object_template.id
    ic(object_template.asdict())
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    ic(response.json())
    assert response.status_code == 201

    response_data = response.json()
    object_id = response_data["Object"]["id"]
    response = client.get(f"/objects/{object_id}", headers=headers)
    response_data = response.json()
    object_data = response_data["Object"]
    assert isinstance(object_data["id"], str)
    assert isinstance(object_data["name"], str)
    await delete_attributes_from_object_resp(db, response_data)


@pytest.mark.asyncio
async def test_delete_object_hard_delete(
    object_data: dict[str, Any],
    db: AsyncSession,
    instance_owner_org,
    object_template,
    event,
    sharing_group,
    site_admin_user_token,
    client,
) -> None:
    object_data["sharing_group_id"] = sharing_group.id
    if object_data["Attribute"]:
        for attribute in object_data["Attribute"]:
            attribute["sharing_group_id"] = sharing_group.id

    object_data["event_id"] = event.id

    await db.commit()

    object_template_id = object_template.id
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 201

    response_data = response.json()
    object_id = response_data["Object"]["id"]
    response = client.delete(f"/objects/{object_id}/true", headers=headers)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["message"] == "Object has been permanently deleted."
    assert response_data["name"] == object_data["name"]
    assert response_data["saved"]
    assert response_data["success"]


@pytest.mark.asyncio
async def test_delete_object_soft_delete(
    object_data: dict[str, Any], db: AsyncSession, sharing_group, object_template, event, site_admin_user_token, client
) -> None:
    object_data["sharing_group_id"] = sharing_group.id
    if object_data["Attribute"]:
        for attribute in object_data["Attribute"]:
            attribute["sharing_group_id"] = sharing_group.id
    object_data["event_id"] = event.id

    await db.commit()

    object_template_id = object_template.id
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 201

    response_data = response.json()
    object_id = response_data["Object"]["id"]
    response_delete = client.delete(f"/objects/{object_id}/false", headers=headers)
    assert response_delete.status_code == 200

    response_delete_data = response_delete.json()
    assert response_delete_data["message"] == "Object has been soft deleted."
    assert response_delete_data["name"] == object_data["name"]
    assert response_delete_data["saved"]
    assert response_delete_data["success"]
    await delete_attributes_from_object_resp(db, response_data)


@pytest.mark.asyncio
async def test_delete_object_invalid_id(site_admin_user_token, client) -> None:
    object_id = "invalid_id"
    headers = {"authorization": site_admin_user_token}
    response_delete = client.delete(f"/objects/{object_id}/true", headers=headers)
    assert response_delete.status_code == 422
    assert "detail" in response_delete.json()


@pytest.mark.asyncio
async def test_delete_object_invalid_hard_delete(
    db, object_data: dict[str, Any], sharing_group, object_template, event, site_admin_user_token, client
) -> None:
    object_data["sharing_group_id"] = sharing_group.id
    if object_data["Attribute"]:
        for attribute in object_data["Attribute"]:
            attribute["sharing_group_id"] = sharing_group.id
    object_data["event_id"] = event.id

    object_template_id = object_template.id
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/objects/{event_id}/{object_template_id}", json=object_data, headers=headers)
    assert response.status_code == 201

    response_data = response.json()
    object_id = response_data["Object"]["id"]
    response_delete = client.delete(f"/objects/{object_id}/invalid_value", headers=headers)
    assert response_delete.status_code == 422
    assert "detail" in response_delete.json()
    await delete_attributes_from_object_resp(db, response_data)
