import random
import string

import pytest
import sqlalchemy as sa

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff
from mmisp.tests.maps import (
    access_test_objects_user_attribute_access_expect_denied,
    access_test_objects_user_attribute_access_expect_granted,
    access_test_objects_user_attribute_edit_expect_denied,
    access_test_objects_user_attribute_edit_expect_granted,
    access_test_objects_user_event_edit_expect_denied,
    access_test_objects_user_event_edit_expect_granted,
)

# @pytest.mark.asyncio
# async def test_get_all_attributes(
#    access_test_objects,
#    client,
# ) -> None:
#    path = "/attributes"
#    request_body = {}
#    clear_key = access_test_objects["default_read_only_user_clear_key"]
#    auth_key = access_test_objects["default_read_only_user_auth_key"]
#
#    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_access_expect_granted)
@pytest.mark.asyncio
async def test_get_existing_attribute_success(access_test_objects, user_key, attribute_key, client) -> None:
    attribute = access_test_objects[attribute_key]
    attribute_id = attribute.id
    print(attribute.asdict())
    path = f"/attributes/{attribute_id}"
    request_body = None
    clear_key = access_test_objects[f"{user_key}_clear_key"]
    auth_key = access_test_objects[f"{user_key}_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_access_expect_denied)
@pytest.mark.asyncio
async def test_get_existing_attribute_fail(
    access_test_objects,
    user_key,
    attribute_key,
    client,
) -> None:
    attribute = access_test_objects[attribute_key]
    attribute_id = attribute.id
    print(attribute.asdict())
    path = f"/attributes/{attribute_id}"
    request_body = None
    clear_key = access_test_objects[f"{user_key}_clear_key"]
    auth_key = access_test_objects[f"{user_key}_auth_key"]

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_edit_expect_granted)
@pytest.mark.asyncio
async def test_delete_existing_attribute(access_test_objects, client, user_key, attribute_key) -> None:
    clear_key = access_test_objects[f"{user_key}_clear_key"]
    auth_key = access_test_objects[f"{user_key}_auth_key"]
    attribute = access_test_objects[attribute_key]
    attribute_id = attribute.id
    request_body = None

    path = f"/attributes/{attribute_id}"
    assert get_legacy_modern_diff("delete", path, request_body, (clear_key, auth_key), client, dry_run=True) == {}


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_edit_expect_denied)
@pytest.mark.asyncio
async def test_delete_existing_attribute_fail(access_test_objects, client, user_key, attribute_key) -> None:
    clear_key = access_test_objects[f"{user_key}_clear_key"]
    auth_key = access_test_objects[f"{user_key}_auth_key"]
    attribute = access_test_objects[attribute_key]
    attribute_id = attribute.id
    request_body = None

    path = f"/attributes/{attribute_id}"
    assert get_legacy_modern_diff("delete", path, request_body, (clear_key, auth_key), client, dry_run=True) == {}


@pytest.mark.parametrize("user_key, event_key", access_test_objects_user_event_edit_expect_granted)
@pytest.mark.asyncio
async def test_add_attribute(db, access_test_objects, client, user_key, event_key) -> None:
    clear_key = access_test_objects[f"{user_key}_clear_key"]
    auth_key = access_test_objects[f"{user_key}_auth_key"]

    random_test = "".join(random.choices(string.ascii_letters, k=20))
    request_body = {
        "value": "1.2.3.4",
        "type": "text",
        "category": "other",
        "to_ids": True,
        "distribution": "1",
        "comment": "test comment",
        "disable_correlation": False,
    }
    event_id = access_test_objects[event_key].id
    path = f"/attributes/{event_id}"
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client, dry_run=True) == {}

    stmt = sa.sql.text("DELETE FROM attributes WHERE value1=:val")
    #    stmt.bindparams(id=response_json["Attribute"]["id"])
    await db.execute(stmt, {"val": random_test})
    await db.commit()


@pytest.mark.parametrize("user_key, event_key", access_test_objects_user_event_edit_expect_denied)
@pytest.mark.asyncio
async def test_add_attribute_fail(access_test_objects, client, user_key, event_key) -> None:
    clear_key = access_test_objects[f"{user_key}_clear_key"]
    auth_key = access_test_objects[f"{user_key}_auth_key"]

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
    path = f"/attributes/{event_id}"
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


# @pytest.mark.asyncio
# async def test_get_all_attributes_read_only_user(
#    access_test_objects,
#    client,
# ) -> None:
#    path = "/attributes"
#    request_body = {}
#    clear_key = access_test_objects["default_read_only_user_clear_key"]
#    auth_key = access_test_objects["default_read_only_user_auth_key"]
#    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


"""
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
"""


# @pytest.mark.asyncio
# async def test_delete_existing_attribute_fail_read_only_user(access_test_objects, client) -> None:
#    attribute_id = access_test_objects["default_attribute"].id
#    path = f"/attributes/{attribute_id}"
#    request_body = {}
#    clear_key = access_test_objects["default_read_only_user_clear_key"]
#    auth_key = access_test_objects["default_read_only_user_auth_key"]
#    assert get_legacy_modern_diff("delete", path, request_body, (clear_key, auth_key), client) == {}


# @pytest.mark.asyncio
# async def test_add_attribute(access_test_objects, client) -> None:
#    request_body = {
#        "value": "1.2.3.4",
#        "type": "ip-src",
#        "category": "Network activity",
#        "to_ids": True,
#        "distribution": "1",
#        "comment": "test comment",
#        "disable_correlation": False,
#    }
#    event_id = access_test_objects["default_event"].id
#    path = f"/attributes/{event_id}"
#    clear_key = access_test_objects["default_user_clear_key"]
#    auth_key = access_test_objects["default_user_auth_key"]
#    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


# @pytest.mark.asyncio
# async def test_add_attribute_fail(access_test_objects, client) -> None:
#    request_body = {
#        "value": "1.2.3.4",
#        "type": "ip-src",
#        "category": "Network activity",
#        "to_ids": True,
#        "distribution": "1",
#        "comment": "test comment",
#        "disable_correlation": False,
#    }
#    event_id = access_test_objects["event_no_access"].id
#    path = f"/attributes/{event_id}"
#    clear_key = access_test_objects["default_user_clear_key"]
#    auth_key = access_test_objects["default_user_auth_key"]
#    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


# @pytest.mark.asyncio
# async def test_add_attribute_fail_read_only_user(access_test_objects, client) -> None:
#    request_body = {
#        "value": "1.2.3.4",
#        "type": "ip-src",
#        "category": "Network activity",
#        "to_ids": True,
#        "distribution": "1",
#        "comment": "test comment",
#        "disable_correlation": False,
#    }
#    event_id = access_test_objects["default_event"].id
#    path = f"/attributes/{event_id}"
#    clear_key = access_test_objects["default_read_only_user_clear_key"]
#    auth_key = access_test_objects["default_read_only_user_auth_key"]
#    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


# @pytest.mark.asyncio
# async def test_add_existing_tag_to_attribute(
#    access_test_objects,
#    client,
# ) -> None:
#    attribute_id = access_test_objects["default_attribute"].id
#    tag_id = access_test_objects["default_tag"].id
#    request_body = None
#    path = f"/attributes/addTag/{attribute_id}/{tag_id}/local:1"
#    clear_key = access_test_objects["default_user_clear_key"]
#    auth_key = access_test_objects["default_user_auth_key"]
#    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


# @pytest.mark.asyncio
# async def test_remove_existing_tag_from_attribute(
#    access_test_objects,
#    client,
# ) -> None:
#    attribute_id = access_test_objects["default_attribute"].id
#    tag_id = access_test_objects["default_tag"].id
#    request_body = None
#    path = f"/attributes/removeTag/{attribute_id}/{tag_id}"
#    clear_key = access_test_objects["default_user_clear_key"]
#    auth_key = access_test_objects["default_user_auth_key"]
#    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


# @pytest.mark.asyncio
# async def test_remove_existing_tag_from_attribute_fail(
#    access_test_objects,
#    client,
# ) -> None:
#    def preprocessor(modern, legacy):
#        if "detail" in modern:
#            modern["errors"] = modern["detail"].get("errors")
#            modern["saved"] = modern["detail"].get("saved")
#            del modern["detail"]
#
#    attribute_id = access_test_objects["attribute_no_access"].id
#    tag_id = access_test_objects["default_tag"].id
#    request_body = None
#    path = f"/attributes/removeTag/{attribute_id}/{tag_id}"
#    clear_key = access_test_objects["default_user_clear_key"]
#    auth_key = access_test_objects["default_user_auth_key"]
#    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client, preprocessor) == {}


# @pytest.mark.asyncio
# async def test_remove_existing_tag_from_attribute_fail_read_only_user(
#    access_test_objects,
#    client,
# ) -> None:
#    attribute_id = access_test_objects["default_attribute"].id
#    tag_id = access_test_objects["default_tag"].id
#    request_body = None
#    path = f"/attributes/removeTag/{attribute_id}/{tag_id}"
#    clear_key = access_test_objects["default_read_only_user_clear_key"]
#    auth_key = access_test_objects["default_read_only_user_auth_key"]
#    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


"""
@pytest.mark.asyncio
async def test_restore_attribute(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute"].id
    request_body = None
    path = f"/attributes/restore/{attribute_id}"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}
"""


# @pytest.mark.asyncio
# async def test_remove_tag_from_attribute(
#    access_test_objects,
#    client,
# ) -> None:
#    attribute_Id = access_test_objects["default_attribute"].id
#    tag_Id = access_test_objects["default_tag"].id
#    headers = {"authorization": access_test_objects["default_user_token"]}
#    client.post(f"/attributes/addTag/{attribute_Id}/{tag_Id}", headers=headers)
#
#    request_body = None
#    path = f"/attributes/removeTag/{attribute_Id}/{tag_Id}"
#    clear_key = access_test_objects["default_user_clear_key"]
#    auth_key = access_test_objects["default_user_auth_key"]
#    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


"""
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
    attribute = access_test_objects["default_attribute"]

    path = f"/attributes/{attribute.id}"
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("put", path, request_body, (clear_key, auth_key), client) == {}
"""


"""
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
"""


# @pytest.mark.asyncio
# async def test_delete_selected_attributes_from_existing_event_fail(access_test_objects, client) -> None:
#    request_body = {"id": "1 2", "allow_hard_delete": False}
#    event_id = access_test_objects["default_event"].id
#
#    attribute_id = access_test_objects["attribute_no_access"].id
#    attribute2_id = access_test_objects["attribute_no_access_2"].id
#    attribute_ids = str(attribute_id) + " " + str(attribute2_id)
#    request_body["id"] = attribute_ids
#    path = f"/attributes/deleteSelected/{event_id}"
#    clear_key = access_test_objects["default_user_clear_key"]
#    auth_key = access_test_objects["default_user_auth_key"]
#    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


# @pytest.mark.asyncio
# async def test_valid_search_attribute_data(access_test_objects, client) -> None:
#    request_body = {"returnFormat": "json", "limit": 100}
#    path = "/attributes/restSearch"
#    clear_key = access_test_objects["default_user_clear_key"]
#    auth_key = access_test_objects["default_user_auth_key"]
#    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}
