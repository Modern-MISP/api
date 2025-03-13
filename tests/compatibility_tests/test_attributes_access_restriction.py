import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_get_all_attributes(
    access_test_objects,
    client,
) -> None:
    path = "/attributes"
    request_body = {}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_get_existing_attribute(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_get_existing_attribute_fail_read_only_user(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_get_existing_attribute_read_only_user_own_org(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["attribute_event_read_only_user"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_get_existing_attribute_fail_read_only_user_own_org(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["attribute_event_read_only_user_2"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_get_existing_attribute_read_only_user_comm(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["attribute_dist_comm"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_get_existing_attribute_fail_read_only_user_comm(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["attribute_dist_comm_2"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_get_existing_attribute_read_only_user_sg(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["attribute_dist_sg"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_get_existing_attribute_fail_read_only_user_sg(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["attribute_dist_sg_2"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_sharing_group_user_clear_key"]
    auth_key = access_test_objects["default_sharing_group_user_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_get_all_attributes_read_only_user(
    access_test_objects,
    client,
) -> None:
    path = "/attributes"
    request_body = {}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_delete_existing_attribute(access_test_objects, client) -> None:
    def preprocessor(modern, legacy):
        if "detail" in modern:
            modern["errors"] = modern["detail"].get("errors")
            modern["saved"] = modern["detail"].get("saved")
            del modern["detail"]

    attribute_id = access_test_objects["default_attribute"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("delete", path, request_body, (clear_key, auth_key), client, preprocessor) == {}


@pytest.mark.asyncio
async def test_delete_existing_attribute_fail_read_only_user(access_test_objects, client) -> None:
    attribute_id = access_test_objects["default_attribute"].id
    path = f"/attributes/{attribute_id}"
    request_body = {}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("delete", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_add_attribute(access_test_objects, client) -> None:
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
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_add_attribute_fail(access_test_objects, client) -> None:
    request_body = {
        "value": "1.2.3.4",
        "type": "ip-src",
        "category": "Network activity",
        "to_ids": True,
        "distribution": "1",
        "comment": "test comment",
        "disable_correlation": False,
    }
    event_id = access_test_objects["event_no_access"].id
    path = f"/attributes/{event_id}"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_add_attribute_fail_read_only_user(access_test_objects, client) -> None:
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
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_add_existing_tag_to_attribute(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute"].id
    tag_id = access_test_objects["default_tag"].id
    request_body = None
    path = f"/attributes/addTag/{attribute_id}/{tag_id}/local:1"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_remove_existing_tag_from_attribute(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute"].id
    tag_id = access_test_objects["default_tag"].id
    request_body = None
    path = f"/attributes/removeTag/{attribute_id}/{tag_id}"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_remove_existing_tag_from_attribute_fail(
    access_test_objects,
    client,
) -> None:
    def preprocessor(modern, legacy):
        if "detail" in modern:
            modern["errors"] = modern["detail"].get("errors")
            modern["saved"] = modern["detail"].get("saved")
            del modern["detail"]

    attribute_id = access_test_objects["attribute_no_access"].id
    tag_id = access_test_objects["default_tag"].id
    request_body = None
    path = f"/attributes/removeTag/{attribute_id}/{tag_id}"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client, preprocessor) == {}


@pytest.mark.asyncio
async def test_remove_existing_tag_from_attribute_fail_read_only_user(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute"].id
    tag_id = access_test_objects["default_tag"].id
    request_body = None
    path = f"/attributes/removeTag/{attribute_id}/{tag_id}"
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_restore_attribute(
    access_test_objects,
    client,
) -> None:
    attribute_Id = access_test_objects["default_attribute"].id
    request_body = None
    path = f"/attributes/restore/{attribute_Id}"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_remove_tag_from_attribute(
    access_test_objects,
    client,
) -> None:
    attribute_Id = access_test_objects["default_attribute"].id
    tag_Id = access_test_objects["default_tag"].id
    headers = {"authorization": access_test_objects["default_user_token"]}
    client.post(f"/attributes/addTag/{attribute_Id}/{tag_Id}", headers=headers)

    request_body = None
    path = f"/attributes/removeTag/{attribute_Id}/{tag_Id}"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_edit_existing_attribute(
    access_test_objects,
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
    attribute = access_test_objects["attribute_dist_sg"]

    path = f"/attributes/{attribute.id}"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("put", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_get_all_attributes_site_admin(
    access_test_objects,
    auth_key,
    client,
) -> None:
    request_body = None
    path = "/attributes"
    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_delete_selected_attributes_from_existing_event(access_test_objects, client) -> None:
    request_body = {"id": "1 2", "allow_hard_delete": False}
    event_id = access_test_objects["default_event"].id
    attribute_id = access_test_objects["default_attribute"].id
    attribute2_id = access_test_objects["default_attribute_2"].id
    attribute_ids = str(attribute_id) + " " + str(attribute2_id)
    request_body["id"] = attribute_ids

    path = f"/attributes/deleteSelected/{event_id}"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_delete_selected_attributes_from_existing_event_fail(access_test_objects, client) -> None:
    request_body = {"id": "1 2", "allow_hard_delete": False}
    event_id = access_test_objects["default_event"].id

    attribute_id = access_test_objects["attribute_no_access"].id
    attribute2_id = access_test_objects["attribute_no_access_2"].id
    attribute_ids = str(attribute_id) + " " + str(attribute2_id)
    request_body["id"] = attribute_ids
    path = f"/attributes/deleteSelected/{event_id}"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_attribute_type_absolute_statistics(access_test_objects, client) -> None:
    request_body = None
    path = "/attributes/attributeStatistics/type/0"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_attribute_type_relative_statistics(access_test_objects, client) -> None:
    request_body = None
    path = "/attributes/attributeStatistics/type/1"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_attribute_category_absolute_statistics(access_test_objects, client) -> None:
    request_body = None
    path = "/attributes/attributeStatistics/category/0"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_attribute_category_relative_statistics(access_test_objects, client) -> None:
    request_body = None
    path = "/attributes/attributeStatistics/category/1"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_valid_search_attribute_data(access_test_objects, client) -> None:
    request_body = {"returnFormat": "json", "limit": 100}
    path = "/attributes/restSearch"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}
