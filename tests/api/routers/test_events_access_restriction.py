import pytest
import respx
import sqlalchemy as sa
from httpx import Response
from icecream import ic
from mmisp.lib.permissions import Permission
from mmisp.api.config import config
from mmisp.db.models.log import Log


@pytest.mark.asyncio
async def test_list_all_events_self_created(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.get("/events", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 3


@pytest.mark.asyncio
async def test_list_all_events_read_only_user(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    response = client.get("/events", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 2


@pytest.mark.asyncio
async def test_list_all_events_admin(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["site_admin_user_token"]}
    response = client.get("/events", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 9


@pytest.mark.asyncio
async def test_get_event_success_read_only_user(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    event_id = access_test_objects["event_read_only_user"].id
    response = client.get(f"/events/{event_id}", headers=headers)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_event_fail_read_only_user(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    event_id = access_test_objects["default_event"].id
    response = client.get(f"/events/{event_id}", headers=headers)

    assert response.status_code == 404  # 403, falls sql filter für legacy misp entfernt werden muss
    # response_json = response.json()
    # assert response_json["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_get_event_fail_read_only_user_not_same_corg(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    event_id = access_test_objects["event_read_only_user_2"].id
    response = client.get(f"/events/{event_id}", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_event_success_read_only_user_comm(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    event_id = access_test_objects["event_dist_comm"].id
    response = client.get(f"/events/{event_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_event_fail_read_only_user_comm(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    event_id = access_test_objects["event_dist_comm_2"].id
    response = client.get(f"/events/{event_id}", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_event_success_read_only_user_sg(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_sharing_group_user_token"]}
    event_id = access_test_objects["event_dist_sg"].id
    response = client.get(f"/events/{event_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_event_fail_read_only_user_sg(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_sharing_group_user_token"]}
    event_id = access_test_objects["event_dist_sg_2"].id
    response = client.get(f"/events/{event_id}", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_event_success_site_admin(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["site_admin_user_token"]}
    event_id = access_test_objects["default_event"].id
    response = client.get(f"/events/{event_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Event"]["id"] == event_id


@pytest.mark.asyncio
async def test_valid_search_attribute_data_read_only_user(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    json = {"returnFormat": "json", "limit": 100}
    response = client.post("/events/restSearch", json=json, headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json["response"], list)
    assert len(response_json) == 1


@pytest.mark.asyncio
async def test_valid_search_attribute_data(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_user_token"]}
    json = {"returnFormat": "json", "limit": 100}
    response = client.post("/events/restSearch", json=json, headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json["response"], list)
    assert len(response_json) == 1


@pytest.mark.asyncio
async def test_valid_search_attribute_data_site_admin(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["site_admin_user_token"]}
    json = {"returnFormat": "json", "limit": 100}
    response = client.post("/events/restSearch", json=json, headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json["response"], list)
    assert len(response_json) == 1


@pytest.mark.asyncio
async def test_publish_existing_event_self_created(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_user_token"]}
    event_id = access_test_objects["default_event_published"].id
    response = client.post(f"/events/publish/{event_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_publish_existing_event_fail_read_only_user(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    event_id = access_test_objects["default_event"].id

    response = client.post(f"/events/publish/{event_id}", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_publish_existing_event_fail(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_user_token"]}
    event_id = access_test_objects["event_no_access"].id
    response = client.post(f"/events/publish/{event_id}", headers=headers)
    assert response.status_code == 200  # if event not found (because can_edit) repsonse is 200 because of check
    response_json = response.json()
    response_json["name"] == "You do not have the permission to do that."
    response_json["message"] == "You do not have the permission to do that."


@pytest.mark.asyncio
async def test_add_existing_tag_to_event(access_test_objects, client) -> None:
    tag_id = access_test_objects["default_tag"].id
    event_id = access_test_objects["default_event"].id

    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.post(f"/events/addTag/{event_id}/{tag_id}/local:1", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_existing_tag_to_event_fail_read_only_user(access_test_objects, client) -> None:
    tag_id = access_test_objects["default_tag"].id
    event_id = access_test_objects["default_event"].id
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    response = client.post(
        f"/events/addTag/{event_id}/{tag_id}/local:1",
        headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 403
    assert response_json["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_add_existing_tag_to_event_fail_read_only_user_no_perms(access_test_objects, client) -> None:
    tag_id = access_test_objects["default_tag"].id
    event_id = access_test_objects["default_event_published"].id
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    response = client.post(
        f"/events/addTag/{event_id}/{tag_id}/local:1",
        headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 403
    assert response_json["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_remove_existing_tag_from_event(access_test_objects, client) -> None:
    tag_id = access_test_objects["default_tag"].id
    event_id = access_test_objects["default_event"].id

    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.post(f"/events/removeTag/{event_id}/{tag_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_remove_existing_tag_from_event_fail_read_only_user(access_test_objects, client) -> None:
    tag_id = access_test_objects["default_tag"].id
    event_id = access_test_objects["default_event"].id
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    response = client.post(f"/events/removeTag/{event_id}/{tag_id}", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_remove_existing_tag_from_event_fail_read_only_user_no_perms(access_test_objects, client) -> None:
    tag_id = access_test_objects["default_tag"].id
    event_id = access_test_objects["default_event_published"].id
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    response = client.post(f"/events/removeTag/{event_id}/{tag_id}", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_edit_existing_event_self_created(access_test_objects, client) -> None:
    request_body = {"info": "updated info"}
    event_id = access_test_objects["default_event"].id
    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.put(f"events/{event_id}", json=request_body, headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_edit_existing_event_suc_read_only_user(access_test_objects, client) -> None:
    request_body = {"info": "updated info"}
    event_id = access_test_objects["event_read_only_user"].id
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    response = client.put(f"events/{event_id}", json=request_body, headers=headers)
    assert response.status_code == 200  # because read only user is in creator org


@pytest.mark.asyncio
async def test_edit_existing_event_fail_wrong_org(access_test_objects, client) -> None:
    request_body = {"info": "updated info"}
    event_id = access_test_objects["event_no_access"].id
    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.put(f"events/{event_id}", json=request_body, headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_existing_event_self_created(access_test_objects, client) -> None:
    event_id = access_test_objects["default_event_published"].id

    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.delete(f"events/{event_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_existing_event_fail_read_only_user(access_test_objects, client) -> None:
    event_id = access_test_objects["default_event"].id
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    response = client.delete(f"events/{event_id}", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_event_valid_data_fail_read_only_user(access_test_objects, client) -> None:
    request_body = {"info": "test event"}
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    response = client.post("/events", json=request_body, headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_publish_existing_event_site_admin(access_test_objects, client) -> None:
    event_id = access_test_objects["default_event"].id

    headers = {"authorization": access_test_objects["site_admin_user_token"]}
    response = client.post(f"/events/publish/{event_id}", headers=headers)
    assert response.status_code == 200
