import pytest
from deepdiff import DeepDiff
from icecream import ic

from mmisp.tests.maps import (
    access_test_objects_user_event_access_expect_denied,
    access_test_objects_user_event_access_expect_granted,
    access_test_objects_user_event_publish_expect_denied,
    access_test_objects_user_event_publish_expect_granted,
    user_to_events,
)


@pytest.mark.parametrize("user_key, event_key", access_test_objects_user_event_access_expect_denied)
@pytest.mark.asyncio
async def test_get_event_fail(access_test_objects, user_key, event_key, client) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    event_id = access_test_objects[event_key].id
    response = client.get(f"/events/{event_id}", headers=headers)

    assert response.status_code == 403


@pytest.mark.parametrize("user_key, event_key", access_test_objects_user_event_access_expect_granted)
@pytest.mark.asyncio
async def test_get_event_success(access_test_objects, user_key, event_key, client) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    event_id = access_test_objects[event_key].id
    response = client.get(f"/events/{event_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Event"]["id"] == event_id


@pytest.mark.parametrize("user_key, events", user_to_events)
@pytest.mark.asyncio
async def test_get_all_events(access_test_objects, user_key, events, client) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    response = client.get("/events/", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    assert isinstance(response_json, list)
    print(response_json)
    event_keys = list(x["info"] for x in response_json)
    diff = DeepDiff(events, event_keys, ignore_order=True, verbose_level=2)
    ic(diff)
    assert diff == {}


# @pytest.mark.asyncio
# async def test_valid_search_attribute_data_read_only_user(access_test_objects, client) -> None:
#    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
#    json = {"returnFormat": "json", "limit": 100}
#    response = client.post("/events/restSearch", json=json, headers=headers)
#    assert response.status_code == 200
#    response_json = response.json()
#    assert isinstance(response_json["response"], list)
#    assert len(response_json) == 1
#
#
# @pytest.mark.asyncio
# async def test_valid_search_attribute_data(access_test_objects, client) -> None:
#    headers = {"authorization": access_test_objects["default_user_token"]}
#    json = {"returnFormat": "json", "limit": 100}
#    response = client.post("/events/restSearch", json=json, headers=headers)
#    assert response.status_code == 200
#    response_json = response.json()
#    assert isinstance(response_json["response"], list)
#    assert len(response_json) == 1
#
#
# @pytest.mark.asyncio
# async def test_valid_search_attribute_data_site_admin(access_test_objects, client) -> None:
#    headers = {"authorization": access_test_objects["site_admin_user_token"]}
#    json = {"returnFormat": "json", "limit": 100}
#    response = client.post("/events/restSearch", json=json, headers=headers)
#    assert response.status_code == 200
#    response_json = response.json()
#    assert isinstance(response_json["response"], list)
#    assert len(response_json) == 1


@pytest.mark.parametrize("user_key, event_key", access_test_objects_user_event_publish_expect_granted)
@pytest.mark.asyncio
async def test_publish_event_success(access_test_objects, user_key, event_key, client) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    event_id = access_test_objects[event_key].id
    response = client.post(f"/events/publish/{event_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.parametrize("user_key, event_key", access_test_objects_user_event_publish_expect_denied)
@pytest.mark.asyncio
async def test_publish_event_fail(access_test_objects, user_key, event_key, client) -> None:
    headers = {"authorization": access_test_objects[f"{user_key}_token"]}
    event_id = access_test_objects[event_key].id
    response = client.post(f"/events/publish/{event_id}", headers=headers)
    assert response.status_code == 403


# Add tag to event

# @pytest.mark.asyncio
# async def test_add_existing_tag_to_event(access_test_objects, client) -> None:
#    tag_id = access_test_objects["default_tag"].id
#    event_id = access_test_objects["default_event"].id
#
#    headers = {"authorization": access_test_objects["default_user_token"]}
#    response = client.post(f"/events/addTag/{event_id}/{tag_id}/local:1", headers=headers)
#    assert response.status_code == 200
#
#
# @pytest.mark.asyncio
# async def test_add_existing_tag_to_event_fail_read_only_user(access_test_objects, client) -> None:
#    tag_id = access_test_objects["default_tag"].id
#    event_id = access_test_objects["default_event"].id
#    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
#    response = client.post(
#        f"/events/addTag/{event_id}/{tag_id}/local:1",
#        headers=headers,
#    )
#    response_json = response.json()
#    assert response.status_code == 403
#    assert response_json["detail"] == "Forbidden"

# Remove tag from  event

# @pytest.mark.asyncio
# async def test_remove_existing_tag_from_event(access_test_objects, client) -> None:
#    tag_id = access_test_objects["default_tag"].id
#    event_id = access_test_objects["default_event"].id
#
#    headers = {"authorization": access_test_objects["default_user_token"]}
#    response = client.post(f"/events/removeTag/{event_id}/{tag_id}", headers=headers)
#    assert response.status_code == 200
#
#
# @pytest.mark.asyncio
# async def test_remove_existing_tag_from_event_fail_read_only_user(access_test_objects, client) -> None:
#    tag_id = access_test_objects["default_tag"].id
#    event_id = access_test_objects["default_event"].id
#    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
#    response = client.post(f"/events/removeTag/{event_id}/{tag_id}", headers=headers)
#    assert response.status_code == 403

# EDIT event

# @pytest.mark.asyncio
# async def test_edit_event_success(access_test_objects, client) -> None:
#    request_body = {"info": "updated info"}
#    event_id = access_test_objects["default_event"].id
#    headers = {"authorization": access_test_objects["default_user_token"]}
#    response = client.put(f"events/{event_id}", json=request_body, headers=headers)
#    assert response.status_code == 200
#
#
# @pytest.mark.asyncio
# async def test_edit_event_fail(access_test_objects, client) -> None:
#    request_body = {"info": "updated info"}
#    event_id = access_test_objects["event_no_access"].id
#    headers = {"authorization": access_test_objects["default_user_token"]}
#    response = client.put(f"events/{event_id}", json=request_body, headers=headers)
#    assert response.status_code == 404
#
## Delete event
#
# @pytest.mark.asyncio
# async def test_delete_event(access_test_objects, client) -> None:
#    event_id = access_test_objects["default_event_published"].id
#
#    headers = {"authorization": access_test_objects["default_user_token"]}
#    response = client.delete(f"events/{event_id}", headers=headers)
#    assert response.status_code == 200
#
#
# @pytest.mark.asyncio
# async def test_delete_event_fail(access_test_objects, client) -> None:
#    event_id = access_test_objects["default_event"].id
#    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
#    response = client.delete(f"events/{event_id}", headers=headers)
#    assert response.status_code == 403
#
## Add Event
# @pytest.mark.asyncio
# async def test_add_event_valid_data_fail_read_only_user(access_test_objects, client) -> None:
#    request_body = {"info": "test event"}
#    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
#    response = client.post("/events", json=request_body, headers=headers)
#    assert response.status_code == 403
