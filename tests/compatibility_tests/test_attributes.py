import pytest

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff
from mmisp.tests.maps import (
    access_test_objects_user_attribute_edit_expect_granted,
)


@pytest.mark.asyncio
async def test_valid_search_attribute_data(access_test_objects, auth_key, client) -> None:
    request_body = {"returnFormat": "json", "limit": 100}
    path = "/attributes/restSearch"
    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.parametrize("user_key, attribute_key", access_test_objects_user_attribute_edit_expect_granted)
@pytest.mark.asyncio
async def test_remove_existing_tag_from_attribute(access_test_objects, client, user_key, attribute_key) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    attribute_id = access_test_objects[attribute_key].id
    tag_id = access_test_objects["default_tag"].id
    response = client.post(f"/attributes/addTag/{attribute_id}/{tag_id}/local:1", headers=headers)
    assert response.status_code == 200

    request_body = None
    clear_key = access_test_objects[f"{user_key}_clear_key"]
    auth_key = access_test_objects[f"{user_key}_auth_key"]

    path = f"/attributes/removeTag/{attribute_id}/{tag_id}"
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client, dry_run=True) == {}


@pytest.mark.asyncio
async def test_update_non_existing_event(db, auth_key, client) -> None:
    path = f"/events/{9999}"

    request_body = {"info": "updated info"}

    assert get_legacy_modern_diff("put", path, request_body, auth_key, client) == {}
