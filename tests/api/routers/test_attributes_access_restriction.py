import pytest
import sqlalchemy as sa
from deepdiff import DeepDiff
from icecream import ic

from mmisp.tests.maps import (
    access_test_objects_user_attribute_access_expect_denied,
    access_test_objects_user_attribute_access_expect_granted,
    access_test_objects_user_attribute_edit_expect_denied,
    access_test_objects_user_attribute_edit_expect_granted,
    access_test_objects_user_event_edit_expect_denied,
    access_test_objects_user_event_edit_expect_granted,
    user_to_attributes,
)


async def remove_attribute_tag(db, attribute_id, tag_id):
    stmt = sa.sql.text("DELETE FROM attribute_tags WHERE tag_id=:tag_id and attribute_id=:attribute_id")
    await db.execute(stmt, {"tag_id": tag_id, "attribute_id": attribute_id})
    await db.commit()


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_access_expect_granted)
@pytest.mark.asyncio
async def test_get_attribute_success(access_test_objects, user_key, attribute_key, client) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    attribute = access_test_objects[attribute_key]
    attribute_id = attribute.id
    print(attribute.asdict())

    response = client.get(f"/attributes/view/{attribute_id}", headers=headers)
    print(response.json())
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Attribute"]["id"] == attribute_id


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_access_expect_denied)
@pytest.mark.asyncio
async def test_get_attribute_fail(access_test_objects, user_key, attribute_key, client) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    attribute_id = access_test_objects[attribute_key].id
    response = client.get(f"/attributes/view/{attribute_id}", headers=headers)

    assert response.status_code == 403


@pytest.mark.parametrize("user_key, attributes", user_to_attributes)
@pytest.mark.asyncio
async def test_get_all_attributes(
    db,
    access_test_objects,
    user_key,
    attributes,
    client,
) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    response = client.get("/attributes?limit=1000", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    #    ic(response_json)
    assert isinstance(response_json, list)
    ic(len(response_json))
    attribute_values = [x["value"] for x in response_json]
    diff = DeepDiff(attributes, attribute_values, ignore_order=True, verbose_level=2)
    ic(diff)
    assert diff == {}


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_edit_expect_granted)
@pytest.mark.asyncio
async def test_delete_existing_attribute(access_test_objects, client, user_key, attribute_key) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    attribute = access_test_objects[attribute_key]
    attribute_id = attribute.id

    response = client.delete(f"/attributes/{attribute_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_edit_expect_denied)
@pytest.mark.asyncio
async def test_delete_existing_attribute_fail(access_test_objects, client, user_key, attribute_key) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    attribute = access_test_objects[attribute_key]
    attribute_id = attribute.id

    response = client.delete(f"/attributes/{attribute_id}", headers=headers)
    assert response.status_code == 403


@pytest.mark.parametrize("user_key, event_key", access_test_objects_user_event_edit_expect_granted)
@pytest.mark.asyncio
async def test_add_attribute(db, access_test_objects, client, user_key, event_key) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    request_body = {
        "value": "1.2.3.4",
        "type": "ip-src",
        "category": "Network activity",
        "to_ids": True,
        "distribution": "1",
        "comment": "test comment",
        "disable_correlation": False,
    }
    event_id = access_test_objects[event_key].id
    response = client.post(f"/attributes/{event_id}", json=request_body, headers=headers)

    assert response.status_code == 200

    stmt = sa.sql.text("DELETE FROM attributes WHERE id=:id")
    #    stmt.bindparams(id=response_json["Attribute"]["id"])
    await db.execute(stmt, {"id": response.json()["Attribute"]["id"]})
    await db.commit()


@pytest.mark.parametrize("user_key, event_key", access_test_objects_user_event_edit_expect_denied)
@pytest.mark.asyncio
async def test_add_attribute_fail(access_test_objects, client, user_key, event_key) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    request_body = {
        "value": "1.2.3.4",
        "type": "ip-src",
        "category": "Network activity",
        "to_ids": True,
        "distribution": "1",
        "comment": "test comment",
        "disable_correlation": False,
    }
    event_id = access_test_objects[event_key].id
    response = client.post(f"/attributes/{event_id}", json=request_body, headers=headers)

    assert response.status_code == 403


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_edit_expect_granted)
@pytest.mark.asyncio
async def test_add_existing_tag_to_attribute(access_test_objects, user_key, attribute_key, client, db) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    attribute_id = access_test_objects[attribute_key].id
    tag_id = access_test_objects["default_tag"].id
    response = client.post(f"/attributes/addTag/{attribute_id}/{tag_id}/local:1", headers=headers)
    assert response.status_code == 200

    await remove_attribute_tag(db, attribute_id, tag_id)


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_edit_expect_granted)
@pytest.mark.asyncio
async def test_remove_existing_tag_from_attribute(access_test_objects, client, user_key, attribute_key) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    attribute_id = access_test_objects[attribute_key].id
    tag_id = access_test_objects["default_tag"].id
    response = client.post(f"/attributes/addTag/{attribute_id}/{tag_id}/local:1", headers=headers)
    assert response.status_code == 200

    response = client.post(f"/attributes/removeTag/{attribute_id}/{tag_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_edit_expect_denied)
@pytest.mark.asyncio
async def test_remove_existing_tag_from_attribute_fail(
    access_test_objects, client, user_key, attribute_key, db
) -> None:
    attribute_id = access_test_objects[attribute_key].id
    tag_id = access_test_objects["default_tag"].id

    headers = {"authorization": access_test_objects["site_admin_user_token"]}
    response = client.post(f"/attributes/addTag/{attribute_id}/{tag_id}/local:1", headers=headers)

    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    response = client.post(f"/attributes/removeTag/{attribute_id}/{tag_id}", headers=headers)
    print(response.json())
    assert response.status_code == 403

    await remove_attribute_tag(db, attribute_id, tag_id)


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_edit_expect_granted)
@pytest.mark.asyncio
async def test_restore_attribute(db, access_test_objects, client, user_key, attribute_key) -> None:
    attribute = access_test_objects[attribute_key]
    attribute_id = attribute.id
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    response = client.delete(f"/attributes/{attribute_id}", headers=headers)

    await db.refresh(attribute)
    assert attribute.deleted

    response = client.post(f"/attributes/restore/{attribute_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Attribute"]["id"] == attribute_id
    assert response_json["Attribute"]["deleted"] is False


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_edit_expect_granted)
@pytest.mark.asyncio
async def test_remove_tag_from_attribute(access_test_objects, client, user_key, attribute_key) -> None:
    attribute_Id = access_test_objects[attribute_key].id
    tag_Id = access_test_objects["default_tag"].id
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    response2 = client.post(f"/attributes/addTag/{attribute_Id}/{tag_Id}", headers=headers)
    response = client.post(f"/attributes/removeTag/{attribute_Id}/{tag_Id}", headers=headers)
    # Der status code liefert immer 200 zurück egal, ob klappt oder wie in diesem Fall fehlschlägt.
    assert response.status_code == 200
    response_json = response.json()
    response2_json = response2.json()
    print(response2_json)
    print(response_json)


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_edit_expect_granted)
@pytest.mark.asyncio
async def test_edit_existing_attribute(access_test_objects, client, user_key, attribute_key) -> None:
    attribute = access_test_objects[attribute_key]

    request_body = {
        "category": "Payload delivery",
        "value": "2.3.4.5",
        "to_ids": True,
        "distribution": "1",
        "comment": "new comment",
        "disable_correlation": False,
    }

    attribute_id = attribute.id
    assert attribute.id is not None

    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    response = client.put(f"/attributes/{attribute_id}", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["Attribute"]["id"] == attribute_id
    assert response_json["Attribute"]["uuid"] == attribute.uuid
    assert "id" in response_json["Attribute"]
    assert "event_id" in response_json["Attribute"]
    assert "object_id" in response_json["Attribute"]
    assert "object_relation" in response_json["Attribute"]
    assert "category" in response_json["Attribute"]
    assert "type" in response_json["Attribute"]
    assert "value" in response_json["Attribute"]
    assert "to_ids" in response_json["Attribute"]
    assert "timestamp" in response_json["Attribute"]
    assert response_json["Attribute"]["distribution"] == 1
    assert response_json["Attribute"]["sharing_group_id"] == 0
    assert "comment" in response_json["Attribute"]
    assert "deleted" in response_json["Attribute"]
    assert "disable_correlation" in response_json["Attribute"]
    assert "first_seen" in response_json["Attribute"]
    assert "last_seen" in response_json["Attribute"]
    assert "Tag" in response_json["Attribute"]
    assert "first_seen" in response_json["Attribute"]

    assert response_json["Attribute"]["first_seen"] is None


@pytest.mark.parametrize("user_key, attributes", user_to_attributes)
@pytest.mark.asyncio
async def test_attribute_type_absolute_statistics(access_test_objects, user_key, attributes, client) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    response = client.get("/attributes/attributeStatistics/type/0", headers=headers)
    assert response.status_code == 200


@pytest.mark.parametrize("user_key, attributes", user_to_attributes)
@pytest.mark.asyncio
async def test_attribute_type_relative_statistics(access_test_objects, user_key, attributes, client) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    response = client.get("/attributes/attributeStatistics/type/1", headers=headers)
    assert response.status_code == 200


@pytest.mark.parametrize("user_key, attributes", user_to_attributes)
@pytest.mark.asyncio
async def test_attribute_category_absolute_statistics(access_test_objects, user_key, attributes, client) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    response = client.get("/attributes/attributeStatistics/category/0", headers=headers)
    assert response.status_code == 200


@pytest.mark.parametrize("user_key, attributes", user_to_attributes)
@pytest.mark.asyncio
async def test_attribute_category_relative_statistics(access_test_objects, user_key, attributes, client) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    response = client.get("/attributes/attributeStatistics/category/1", headers=headers)
    assert response.status_code == 200
