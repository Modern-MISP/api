import pytest
import sqlalchemy as sa

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_attribute_type_absolute_statistics(access_test_objects, auth_key, client) -> None:
    path = "/attributes/attributeStatistics/type/0"
    request_body = None
    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_attribute_type_relative_statistics(access_test_objects, auth_key, client) -> None:
    path = "/attributes/attributeStatistics/type/1"
    request_body = None
    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_attribute_category_absolute_statistics(access_test_objects, auth_key, client) -> None:
    path = "/attributes/attributeStatistics/category/0"
    request_body = None
    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_attribute_category_relative_statistics(access_test_objects, auth_key, client) -> None:
    request_body = None
    path = "/attributes/attributeStatistics/category/1"
    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_valid_search_attribute_data(access_test_objects, auth_key, client) -> None:
    request_body = {"returnFormat": "json", "limit": 100}
    path = "/attributes/restSearch"
    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


"""
@pytest.mark.asyncio
async def test_add_attribute_valid_data(access_test_objects, auth_key, client) -> None:
    request_body = {
        "value": "1.2.3.4",
        "type": "ip-src",
        "category": "Network activity",
        "to_ids": True,
        "distribution": "1",
        "comment": "test comment",
        "disable_correlation": False,
    }

    event_id = access_test_objects["default_event"].id

    path = f"/attributes/{event_id}"

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}

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
"""


@pytest.mark.asyncio
async def test_delete_existing_attribute(
    access_test_objects,
    auth_key,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute_2"].id
    request_body = None
    path = f"/attributes/{attribute_id}"
    assert get_legacy_modern_diff("delete", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_restore_attribute_site_admin(
    access_test_objects,
    auth_key,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute_2"].id
    request_body = None
    path = f"/attributes/restore/{attribute_id}"
    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}


"""
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
"""


@pytest.mark.asyncio
async def test_remove_existing_tag_from_attribute(
    access_test_objects,
    auth_key,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute"].id
    tag_id = access_test_objects["default_tag_2"].id
    request_body = None
    path = f"/attributes/removeTag/{attribute_id}/{tag_id}"
    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_edit_existing_attribute(
    access_test_objects,
    auth_key,
    client,
) -> None:
    request_body = {
        "category": "Payload delivery",
        "value": "2.3.4.5",
        "to_ids": True,
        "distribution": "1",
        "comment": "new comment",
        "disable_correlation": False,
        "first_seen": "",
    }
    attribute = access_test_objects["default_attribute_2"]
    path = f"/attributes/{attribute.id}"
    assert get_legacy_modern_diff("put", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_update_non_existing_event(db, auth_key, client) -> None:
    path = f"/events/{9999}"

    request_body = {"info": "updated info"}

    assert get_legacy_modern_diff("put", path, request_body, auth_key, client) == {}
