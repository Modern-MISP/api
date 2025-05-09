import uuid

import pytest
import pytest_asyncio
import sqlalchemy as sa
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.db.models.attribute import AttributeTag
from mmisp.tests.generators.model_generators.tag_generator import generate_tag


async def remove_attribute_tag(db, attribute_id, tag_id):
    stmt = sa.sql.text("DELETE FROM attribute_tags WHERE tag_id=:tag_id and attribute_id=:attribute_id")
    await db.execute(stmt, {"tag_id": tag_id, "attribute_id": attribute_id})
    await db.commit()


@pytest_asyncio.fixture
async def attributetag(attribute, event, tag, db):
    attribute_tag = AttributeTag(attribute_id=attribute.id, event_id=event.id, tag_id=tag.id, local=False)

    db.add(attribute_tag)
    await db.commit()

    yield attribute_tag

    await db.delete(attribute_tag)
    await db.commit()


@pytest.mark.asyncio
async def test_add_attribute_valid_data(site_admin_user_token, event, db, client) -> None:
    request_body = {
        "value": "1.2.3.4",
        "type": "ip-src",
        "category": "Network activity",
        "to_ids": True,
        "distribution": 1,
        "comment": "test comment",
        "disable_correlation": False,
    }
    event_id = event.id
    assert event.id is not None

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/attributes/{event_id}", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Attribute"]["value"] == request_body["value"]
    assert response_json["Attribute"]["type"] == request_body["type"]
    assert response_json["Attribute"]["category"] == request_body["category"]
    assert response_json["Attribute"]["to_ids"] == request_body["to_ids"]
    assert response_json["Attribute"]["distribution"] == request_body["distribution"]
    assert response_json["Attribute"]["comment"] == request_body["comment"]
    assert response_json["Attribute"]["disable_correlation"] == request_body["disable_correlation"]
    assert response_json["Attribute"]["id"] is not None
    assert uuid.UUID(response_json["Attribute"]["uuid"])

    # need to remove attribute, so teardown works
    stmt = sa.sql.text("DELETE FROM attributes WHERE id=:id")
    await db.execute(stmt, {"id": response_json["Attribute"]["id"]})
    await db.commit()


@pytest.mark.asyncio
async def test_add_attribute_valid_data_by_event_uuid(site_admin_user_token, event, db, client) -> None:
    request_body = {
        "value": "1.2.3.4",
        "type": "ip-src",
        "category": "Network activity",
        "to_ids": True,
        "distribution": 1,
        "comment": "test comment",
        "disable_correlation": False,
    }
    event_uuid = event.uuid
    assert event_uuid is not None

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/attributes/{event_uuid}", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Attribute"]["value"] == request_body["value"]
    assert response_json["Attribute"]["type"] == request_body["type"]
    assert response_json["Attribute"]["category"] == request_body["category"]
    assert response_json["Attribute"]["to_ids"] == request_body["to_ids"]
    assert response_json["Attribute"]["distribution"] == request_body["distribution"]
    assert response_json["Attribute"]["comment"] == request_body["comment"]
    assert response_json["Attribute"]["disable_correlation"] == request_body["disable_correlation"]
    assert response_json["Attribute"]["id"] is not None
    assert uuid.UUID(response_json["Attribute"]["uuid"])

    # need to remove attribute, so teardown works
    print(response_json["Attribute"]["id"])
    stmt = sa.sql.text("DELETE FROM attributes WHERE id=:id")
    #    stmt.bindparams(id=response_json["Attribute"]["id"])
    await db.execute(stmt, {"id": response_json["Attribute"]["id"]})
    await db.commit()


@pytest.mark.asyncio
async def test_add_attribute_invalid_event_id(site_admin_user_token, client) -> None:
    request_body = {
        "value": "1.2.3.4",
        "type": "ip-src",
        "category": "Network activity",
        "to_ids": True,
        "distribution": 1,
        "comment": "test comment",
        "disable_correlation": False,
    }
    headers = {"authorization": site_admin_user_token}
    response = client.post(
        "/attributes/0",
        json=request_body,
        headers=headers,
    )
    ic(response)
    assert response.status_code == 404

    response = client.post(
        "/attributes/999999999",
        json=request_body,
        headers=headers,
    )
    ic(response)
    assert response.status_code == 404

    response = client.post(
        "/attributes/a469325efe2f4f32a6854579f415ec6a",
        json=request_body,
        headers=headers,
    )
    ic(response)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_attribute_invalid_data(
    db: AsyncSession, event, site_admin_user_token, sharing_group, client
) -> None:
    request_body = {"value": "1.2.3.4", "type": "invalid"}

    event.sharing_group_id = sharing_group.id

    await db.commit()

    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/attributes/{event_id}", json=request_body, headers=headers)
    ic(response.json())
    assert response.status_code == 422


# --- Test get attribute by id
@pytest.mark.asyncio
async def test_get_existing_attribute(
    db: AsyncSession,
    attribute_with_normal_tag,
    site_admin_user_token,
    client,
) -> None:
    attribute, at = attribute_with_normal_tag
    attribute_id = attribute.id

    ic(attribute.asdict())

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/attributes/{attribute_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    ic(response_json)
    assert response_json["Attribute"]["id"] == attribute_id
    assert response_json["Attribute"]["event_id"] == attribute.event_id
    assert "id" in response_json["Attribute"]
    assert "event_id" in response_json["Attribute"]
    assert "object_id" in response_json["Attribute"]
    assert "object_relation" in response_json["Attribute"]
    assert "category" in response_json["Attribute"]
    assert "type" in response_json["Attribute"]
    assert "value" in response_json["Attribute"]
    assert "to_ids" in response_json["Attribute"]
    assert "uuid" in response_json["Attribute"]
    assert "timestamp" in response_json["Attribute"]
    assert "distribution" in response_json["Attribute"]
    assert "sharing_group_id" in response_json["Attribute"]
    assert "comment" in response_json["Attribute"]
    assert "deleted" in response_json["Attribute"]
    assert "disable_correlation" in response_json["Attribute"]
    assert "first_seen" in response_json["Attribute"]
    assert "last_seen" in response_json["Attribute"]
    assert "event_uuid" in response_json["Attribute"]
    assert "Tag" in response_json["Attribute"]
    if len(response_json["Attribute"]["Tag"]) > 0:
        print(response_json["Attribute"]["Tag"])
        assert response_json["Attribute"]["Tag"][0]["id"] == at.id


# --- Test get attribute by uuid
@pytest.mark.asyncio
async def test_get_existing_attribute_by_uuid(
    db: AsyncSession,
    attribute_with_normal_tag,
    site_admin_user_token,
    client,
) -> None:
    attribute, at = attribute_with_normal_tag
    attribute_uuid = attribute.uuid

    ic(attribute.asdict())

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/attributes/{attribute_uuid}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    ic(response_json)
    assert response_json["Attribute"]["uuid"] == attribute.uuid
    assert response_json["Attribute"]["event_id"] == attribute.event_id
    assert "id" in response_json["Attribute"]
    assert "event_id" in response_json["Attribute"]
    assert "object_id" in response_json["Attribute"]
    assert "object_relation" in response_json["Attribute"]
    assert "category" in response_json["Attribute"]
    assert "type" in response_json["Attribute"]
    assert "value" in response_json["Attribute"]
    assert "to_ids" in response_json["Attribute"]
    assert "timestamp" in response_json["Attribute"]
    assert "distribution" in response_json["Attribute"]
    assert "sharing_group_id" in response_json["Attribute"]
    assert "comment" in response_json["Attribute"]
    assert "deleted" in response_json["Attribute"]
    assert "disable_correlation" in response_json["Attribute"]
    assert "first_seen" in response_json["Attribute"]
    assert "last_seen" in response_json["Attribute"]
    assert "event_uuid" in response_json["Attribute"]
    assert "Tag" in response_json["Attribute"]
    if len(response_json["Attribute"]["Tag"]) > 0:
        print(response_json["Attribute"]["Tag"])
        assert response_json["Attribute"]["Tag"][0]["id"] == at.id


@pytest.mark.asyncio
async def test_get_invalid_or_non_existing_attribute(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/attributes/0", headers=headers)
    assert response.status_code == 404

    response = client.get("/attributes/a469325efe2f4f32a6854579f415ec6a", headers=headers)
    assert response.status_code == 404

    response = client.get("/attributes/invalid_id", headers=headers)
    assert response.status_code == 422


# --- Test edit attribute
@pytest.mark.asyncio
async def test_edit_existing_attribute(
    db: AsyncSession, site_admin_user_token, sharing_group, event, attribute, client
) -> None:
    request_body = {
        "category": "Payload delivery",
        "value": "2.3.4.5",
        "to_ids": True,
        "distribution": 1,
        "comment": "new comment",
        "disable_correlation": False,
    }
    event.sharing_group_id = sharing_group.id
    await db.commit()

    event_id = event.id

    attribute.sharing_group_id = sharing_group.id

    await db.commit()

    attribute_id = attribute.id
    assert attribute.id is not None

    headers = {"authorization": site_admin_user_token}
    response = client.put(f"/attributes/{attribute_id}", json=request_body, headers=headers)

    if response.status_code != 200:
        print(response.json())

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["Attribute"]["id"] == attribute_id
    assert response_json["Attribute"]["event_id"] == event_id
    assert "id" in response_json["Attribute"]
    assert "event_id" in response_json["Attribute"]
    assert "object_id" in response_json["Attribute"]
    assert "object_relation" in response_json["Attribute"]
    assert "category" in response_json["Attribute"]
    assert "type" in response_json["Attribute"]
    assert "value" in response_json["Attribute"]
    assert "to_ids" in response_json["Attribute"]
    assert "uuid" in response_json["Attribute"]
    assert "timestamp" in response_json["Attribute"]
    assert "distribution" in response_json["Attribute"]
    assert "sharing_group_id" in response_json["Attribute"]
    assert "comment" in response_json["Attribute"]
    assert "deleted" in response_json["Attribute"]
    assert "disable_correlation" in response_json["Attribute"]
    #    assert "first_seen" in response_json["Attribute"]
    assert "last_seen" in response_json["Attribute"]
    assert "Tag" in response_json["Attribute"]
    #    assert "first_seen" in response_json["Attribute"]


#    assert response_json["Attribute"]["first_seen"] is None


@pytest.mark.asyncio
async def test_edit_existing_attribute_by_uuid(
    db: AsyncSession, site_admin_user_token, sharing_group, event, attribute, client
) -> None:
    request_body = {
        "category": "Payload delivery",
        "value": "2.3.4.5",
        "to_ids": True,
        "distribution": 1,
        "comment": "new comment",
        "disable_correlation": False,
    }
    event.sharing_group_id = sharing_group.id
    await db.commit()

    event_id = event.id

    attribute.sharing_group_id = sharing_group.id

    await db.commit()

    attribute_uuid = attribute.uuid
    assert attribute.id is not None

    headers = {"authorization": site_admin_user_token}
    response = client.put(f"/attributes/{attribute_uuid}", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["Attribute"]["uuid"] == attribute_uuid
    assert response_json["Attribute"]["event_id"] == event_id
    assert "id" in response_json["Attribute"]
    assert "event_id" in response_json["Attribute"]
    assert "object_id" in response_json["Attribute"]
    assert "object_relation" in response_json["Attribute"]
    assert "category" in response_json["Attribute"]
    assert "type" in response_json["Attribute"]
    assert "value" in response_json["Attribute"]
    assert "to_ids" in response_json["Attribute"]
    assert "uuid" in response_json["Attribute"]
    assert "timestamp" in response_json["Attribute"]
    assert "distribution" in response_json["Attribute"]
    assert "sharing_group_id" in response_json["Attribute"]
    assert "comment" in response_json["Attribute"]
    assert "deleted" in response_json["Attribute"]
    assert "disable_correlation" in response_json["Attribute"]
    assert "first_seen" in response_json["Attribute"]
    assert "last_seen" in response_json["Attribute"]
    assert "Tag" in response_json["Attribute"]
    assert "first_seen" in response_json["Attribute"]

    assert response_json["Attribute"]["first_seen"] is None


@pytest.mark.asyncio
async def test_edit_non_existing_attribute(site_admin_user_token, client) -> None:
    request_body = {
        "category": "Payload delivery",
        "value": "2.3.4.5",
        "to_ids": True,
        "distribution": 1,
        "comment": "new comment",
        "disable_correlation": False,
    }
    headers = {"authorization": site_admin_user_token}
    response = client.put("/attributes/0", json=request_body, headers=headers)
    assert response.status_code == 404
    response = client.put("/attributes/999999999", json=request_body, headers=headers)
    assert response.status_code == 404
    response = client.get("/attributes/a469325efe2f4f32a6854579f415ec6a", headers=headers)
    assert response.status_code == 404


# --- Test delete attribute by id
@pytest.mark.asyncio
async def test_delete_existing_attribute(
    db: AsyncSession, instance_org_two, site_admin_user_token, sharing_group, organisation, event, attribute, client
) -> None:
    event.sharing_group_id = sharing_group.id

    setattr(attribute, "sharing_group_id", sharing_group.id)

    await db.commit()

    attribute_id = attribute.id

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/attributes/{attribute_id}", headers=headers)

    assert response.status_code == 200

    # --- Test delete attribute by id


@pytest.mark.asyncio
async def test_delete_existing_attribute_by_uuid(
    db: AsyncSession, instance_org_two, site_admin_user_token, sharing_group, organisation, event, attribute, client
) -> None:
    event.sharing_group_id = sharing_group.id

    setattr(attribute, "sharing_group_id", sharing_group.id)

    await db.commit()

    attribute_uuid = attribute.uuid

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/attributes/{attribute_uuid}", headers=headers)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_invalid_or_non_existing_attribute(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete("/attributes/0", headers=headers)
    assert response.status_code == 404
    response = client.delete("/attributes/invalid_id", headers=headers)
    assert response.status_code == 422
    response = client.get("/attributes/a469325efe2f4f32a6854579f415ec6a", headers=headers)
    assert response.status_code == 404


# --- Test get all attributes


@pytest.mark.asyncio
async def test_get_all_attributes(
    db: AsyncSession, event, site_admin_user_token, sharing_group, organisation, attribute, attribute2, client
) -> None:
    event.sharing_group_id = sharing_group.id
    attribute.sharing_group_id = sharing_group.id
    attribute2.sharing_group_id = sharing_group.id

    await db.commit()

    headers = {"authorization": site_admin_user_token}
    response = client.get("/attributes", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    for attribute in response_json:
        assert isinstance(response_json, list)
        assert "id" in attribute
        assert "event_id" in attribute
        assert "object_id" in attribute
        assert "object_relation" in attribute
        assert "category" in attribute
        assert "type" in attribute
        assert "value" in attribute
        assert "value1" in attribute
        assert "value2" in attribute
        assert "to_ids" in attribute
        assert "uuid" in attribute
        assert "timestamp" in attribute
        assert "distribution" in attribute
        assert "sharing_group_id" in attribute
        assert "comment" in attribute
        assert "deleted" in attribute
        assert "disable_correlation" in attribute
        assert "first_seen" in attribute
        assert "last_seen" in attribute


# --- Test attribute statistics


@pytest.mark.asyncio
async def test_attribute_type_absolute_statistics(event, attribute, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/attributes/attributeStatistics/type/0", headers=headers)
    assert response.status_code == 200
    response_json = response.json()

    assert attribute.type in response_json.keys()


@pytest.mark.asyncio
async def test_attribute_type_relative_statistics(event, attribute, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/attributes/attributeStatistics/type/1", headers=headers)
    assert response.status_code == 200
    response_json = response.json()

    assert attribute.type in response_json.keys()
    for _, v in response_json.items():
        assert "%" in v


@pytest.mark.asyncio
async def test_attribute_category_absolute_statistics(event, attribute, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/attributes/attributeStatistics/category/0", headers=headers)
    assert response.status_code == 200
    response_json = response.json()

    assert attribute.category in response_json.keys()


@pytest.mark.asyncio
async def test_attribute_category_relative_statistics(event, attribute, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/attributes/attributeStatistics/category/1", headers=headers)
    assert response.status_code == 200
    response_json = response.json()

    assert attribute.category in response_json.keys()
    for _, v in response_json.items():
        assert "%" in v


@pytest.mark.asyncio
async def test_invalid_parameters_attribute_statistics(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/attributes/attributeStatistics/type/non_boolean", headers=headers)
    assert response.status_code == 422


# --- Test attribute describe types


@pytest.mark.asyncio
async def test_attribute_describe_types(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/attributes/describeTypes", headers=headers)
    assert response.status_code == 200


# --- Test restore attribute


@pytest.mark.asyncio
async def test_restore_existing_attribute(
    db: AsyncSession, site_admin_user_token, sharing_group, event, attribute, client
) -> None:
    event.sharing_group_id = sharing_group.id

    db.add(event)
    await db.commit()
    await db.refresh(event)

    attribute.sharing_group_id = sharing_group.id

    await db.commit()

    attribute_id = attribute.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/attributes/restore/{attribute_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_restore_existing_attribute_by_uuid(
    db: AsyncSession, site_admin_user_token, sharing_group, event, attribute, client
) -> None:
    event.sharing_group_id = sharing_group.id

    db.add(event)
    await db.commit()
    await db.refresh(event)

    attribute.sharing_group_id = sharing_group.id

    await db.commit()

    attribute_uuid = attribute.uuid

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/attributes/restore/{attribute_uuid}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_restore_invalid_attribute(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/attributes/restore/0", headers=headers)
    assert response.status_code == 404
    response = client.post("/attributes/restore/invalid_id", headers=headers)
    assert response.status_code == 422
    response = client.post("/attributes/restore/a469325efe2f4f32a6854579f415ec6a", headers=headers)
    assert response.status_code == 404


# --- Test adding a tag


@pytest.mark.asyncio
async def test_add_existing_tag_to_attribute(
    db: AsyncSession, site_admin_user_token, sharing_group, event, attribute, client
) -> None:
    event.sharing_group_id = sharing_group.id

    setattr(attribute, "sharing_group_id", sharing_group.id)

    await db.commit()

    attribute_id = attribute.id

    tag = generate_tag()
    setattr(tag, "user_id", 1)
    setattr(tag, "org_id", 1)

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    tag_id = tag.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(
        f"/attributes/addTag/{attribute_id}/{tag_id}/local:1",
        headers=headers,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["success"] == "Tag added"
    assert response_json["check_publish"]

    await remove_attribute_tag(db, attribute_id, tag_id)


@pytest.mark.asyncio
async def test_add_existing_tag_to_attribute_by_uuid(
    db: AsyncSession, site_admin_user_token, sharing_group, event, attribute, client
) -> None:
    event.sharing_group_id = sharing_group.id

    setattr(attribute, "sharing_group_id", sharing_group.id)

    await db.commit()

    attribute_uuid = attribute.uuid
    attribute_id = attribute.id

    tag = generate_tag()
    setattr(tag, "user_id", 1)
    setattr(tag, "org_id", 1)

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    tag_id = tag.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(
        f"/attributes/addTag/{attribute_uuid}/{tag_id}/local:1",
        headers=headers,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["success"] == "Tag added"
    assert response_json["check_publish"]

    await remove_attribute_tag(db, attribute_id, tag_id)


@pytest.mark.asyncio
async def test_add_invalid_or_non_existing_tag_to_attribute(
    db: AsyncSession, site_admin_user_token, event, sharing_group, attribute, client
) -> None:
    event.sharing_group_id = sharing_group.id
    attribute.sharing_group_id = sharing_group.id

    await db.commit()

    attribute_id = attribute.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(
        f"/attributes/addTag/{attribute_id}/0/local:0",
        headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"] is False
    response = client.post(
        f"/attributes/addTag/{attribute_id}/invalid_id/local:1",
        headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"] is False


@pytest.mark.asyncio
async def test_add_invalid_or_non_existing_tag_to_attribute_by_uuid(
    db: AsyncSession, site_admin_user_token, event, sharing_group, attribute, client
) -> None:
    event.sharing_group_id = sharing_group.id
    attribute.sharing_group_id = sharing_group.id

    await db.commit()

    attribute_uuid = attribute.uuid

    headers = {"authorization": site_admin_user_token}
    response = client.post(
        f"/attributes/addTag/{attribute_uuid}/0/local:0",
        headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"] is False
    response = client.post(
        f"/attributes/addTag/{attribute_uuid}/invalid_id/local:1",
        headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"] is False


@pytest.mark.asyncio
async def test_remove_existing_tag_from_attribute(
    db: AsyncSession, site_admin_user_token, attributetag, client
) -> None:
    attribute_id = attributetag.attribute_id
    tag_id = attributetag.tag_id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/attributes/removeTag/{attribute_id}/{tag_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    ic(response_json)
    assert response_json["saved"]
    assert response_json["success"] == "Tag removed."


@pytest.mark.asyncio
async def test_remove_existing_tag_from_attribute_by_uuid(
    db: AsyncSession, site_admin_user_token, attribute, attributetag, client
) -> None:
    attribute_uuid = attribute.uuid
    tag_id = attributetag.tag_id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/attributes/removeTag/{attribute_uuid}/{tag_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    ic(response_json)
    assert response_json["saved"]
    assert response_json["success"] == "Tag removed."
