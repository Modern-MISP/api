import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff
from mmisp.tests.maps import (
    access_test_objects_user_event_access_expect_denied,
    access_test_objects_user_event_access_expect_granted,
)

"""
@pytest.mark.asyncio
async def test_list_all_events_self_created(access_test_objects, client) -> None:
    path = "/events"
    request_body = None
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    print("SharingGroup: ", access_test_objects["default_sharing_group"].__dict__)

    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_list_all_events_read_only_user(access_test_objects, client) -> None:
    path = "/events"
    request_body = None
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}
"""


@pytest.mark.asyncio
async def test_list_all_events_admin(auth_key, client) -> None:
    path = "/events"
    request_body = {}
    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.parametrize("user_key, event_key", access_test_objects_user_event_access_expect_granted)
@pytest.mark.asyncio
async def test_get_event_success(access_test_objects, user_key, event_key, client) -> None:
    path = f"/events/{access_test_objects[event_key].id}"
    request_body = None
    clear_key = access_test_objects[f"{user_key}_clear_key"]
    auth_key = access_test_objects[f"{user_key}_auth_key"]
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.parametrize("user_key, event_key", access_test_objects_user_event_access_expect_denied)
@pytest.mark.asyncio
async def test_get_event_fail(access_test_objects, user_key, event_key, client) -> None:
    path = f"/events/{access_test_objects[event_key].id}"
    request_body = None
    clear_key = access_test_objects[f"{user_key}_clear_key"]
    auth_key = access_test_objects[f"{user_key}_auth_key"]
    assert get_legacy_modern_diff("get", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_valid_search_attribute_data_read_only_user(db: AsyncSession, access_test_objects, client) -> None:
    def preprocess(modern, legacy):
        del modern["response"][0]["Event"]["Tag"]
        del modern["response"][0]["Event"]["Attribute"][0]["Tag"]
        del modern["response"][2]["Event"]["event_creator_email"]

    path = "/events/restSearch"
    request_body = {"returnFormat": "json", "limit": 100, "distribution": 0}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client, preprocess) == {}


"""
@pytest.mark.asyncio
async def test_valid_search_attribute_data(
    db:AsyncSession, access_test_objects, client) -> None:
    def preprocess(modern, legacy):
        del modern["response"][0]["Event"]["Tag"]
        del modern["response"][0]["Event"]["Attribute"][0]["Tag"]
        del modern["response"][1]["Event"]["Tag"]
        del modern["response"][2]["Event"]["Tag"]
        del modern["response"][2]["Event"]["Attribute"][0]["Tag"]
        del modern['response'][0]['Event']['event_creator_email']
        del modern['response'][1]['Event']['event_creator_email']
        del modern['response'][2]['Event']['event_creator_email']

    path = "/events/restSearch"
    request_body = {"returnFormat": "json", "limit": 100, "distribution": 0}
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client, preprocess) == {}
"""


@pytest.mark.asyncio
async def test_publish_existing_event_self_created(access_test_objects, client) -> None:
    path = "/events/publish/" + str(access_test_objects["default_event_published"].id)
    request_body = {"distribution": 0}
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_publish_existing_event_fail_read_only_user(access_test_objects, client) -> None:
    path = "/events/publish/" + str(access_test_objects["default_event_published"].id)
    request_body = {"returnFormat": "json", "limit": 100, "distribution": 0}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_publish_existing_event_fail(access_test_objects, client) -> None:
    path = "/events/publish/" + str(access_test_objects["event_no_access"].id)
    request_body = {"distribution": 0}
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


# @pytest.mark.asyncio
# async def test_add_existing_tag_to_event(access_test_objects, client) -> None:
#    tag_id = access_test_objects["default_tag"].id
#    event_id = access_test_objects["default_event"].id
#    path = "/events/addTag/" + str(event_id) + "/" + str(tag_id) + "/local:1"
#    request_body = {"distribution": 0}
#    clear_key = access_test_objects["default_user_clear_key"]
#    auth_key = access_test_objects["default_user_auth_key"]
#    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_add_existing_tag_to_event_fail_read_only_user(access_test_objects, client) -> None:
    tag_id = access_test_objects["default_tag"].id
    event_id = access_test_objects["default_event"].id
    path = "/events/addTag/" + str(event_id) + "/" + str(tag_id) + "/local:1"
    request_body = {"distribution": 0}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_add_existing_tag_to_event_fail_read_only_user_no_perms(access_test_objects, client) -> None:
    tag_id = access_test_objects["default_tag"].id
    event_id = access_test_objects["default_event_published"].id
    path = "/events/addTag/" + str(event_id) + "/" + str(tag_id) + "/local:1"
    request_body = {"distribution": 0}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_remove_existing_tag_from_event(access_test_objects, client) -> None:
    tag_id = access_test_objects["default_tag"].id
    event_id = access_test_objects["default_event"].id
    path = "/events/removeTag/" + str(event_id) + "/" + str(tag_id)
    request_body = {"distribution": 0}
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_remove_existing_tag_from_event_fail_read_only_user(access_test_objects, client) -> None:
    tag_id = access_test_objects["default_tag"].id
    event_id = access_test_objects["default_event"].id
    path = "/events/removeTag/" + str(event_id) + "/" + str(tag_id)
    request_body = {"distribution": 0}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_remove_existing_tag_from_event_fail_read_only_user_no_perms(access_test_objects, client) -> None:
    tag_id = access_test_objects["default_tag"].id
    event_id = access_test_objects["default_event_published"].id
    path = "/events/removeTag/" + str(event_id) + "/" + str(tag_id)
    request_body = {"distribution": 0}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


"""
@pytest.mark.asyncio
async def test_edit_existing_event_self_created(access_test_objects, client) -> None:
    event_id = access_test_objects["default_event"].id
    path = "/events/" + str(event_id)
    request_body = {"info": "updated info"}
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("put", path, request_body, (clear_key, auth_key), client) == {}
"""


@pytest.mark.asyncio
async def test_edit_existing_event_fail_wrong_org(access_test_objects, client) -> None:
    event_id = access_test_objects["event_no_access"].id
    path = "/events/" + str(event_id)
    request_body = {"info": "updated info"}
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("put", path, request_body, (clear_key, auth_key), client) == {}


"""
@pytest.mark.asyncio
async def test_delete_existing_event_self_created(access_test_objects, client) -> None:
    event_id = access_test_objects["default_event_published"].id
    path = "/events/" + str(event_id)
    request_body = None
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("delete", path, request_body, (clear_key, auth_key), client) == {}
"""


@pytest.mark.asyncio
async def test_delete_existing_event_fail_read_only_user(access_test_objects, client) -> None:
    event_id = access_test_objects["default_event"].id
    path = "/events/" + str(event_id)
    request_body = None
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("delete", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_add_event_valid_data_fail_read_only_user(access_test_objects, client) -> None:
    path = "/events"
    request_body = {"info": "test event"}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client) == {}


@pytest.mark.asyncio
async def test_publish_existing_event_site_admin(access_test_objects, auth_key, client) -> None:
    event_id = access_test_objects["default_event"].id
    path = "/events/publish/" + str(event_id)
    request_body = None
    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}
