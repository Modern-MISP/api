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
    assert len(response_json) == 2


@pytest.mark.asyncio
async def test_list_all_events_read_only_user(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    response = client.get("/events", headers=headers)
    assert response.status_code == 200

    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 1


@pytest.mark.asyncio
async def test_list_all_events_admin(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["site_admin_user_token"]}
    response = client.get("/events", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 4


@pytest.mark.asyncio
async def test_get_event_success_read_only_user(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    event_id = access_test_objects["default_event_published"].id
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
    evnt = access_test_objects["event_no_access"]
    usr = access_test_objects["default_user"]
    print("EventID: ", event_id)
    print("User ID: ", usr.id)
    print("User orgID: ", usr.org_id)
    print("User siteadmin: ", usr.role.check_permission(Permission.SITE_ADMIN))
    print("User modify: ", usr.role.check_permission(Permission.MODIFY))
    print("User modifyOrg: ", usr.role.check_permission(Permission.MODIFY_ORG))

    print("Event UserID:", evnt.user_id)
    print("Event orgID:", evnt.org_id)
    print("Event orgcID:", evnt.orgc_id)
    print("Event canEdit:", evnt.can_edit(usr))

    response = client.post(f"/events/publish/{event_id}", headers=headers)
    assert response.status_code == 403


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
async def test_remove_existing_tag_from_event_fail_read_only_user(
    access_test_objects, role_read_modify_only, event5, tag, read_only_user_token, client
) -> None:
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
async def test_edit_existing_event_read_only_user(
    site_admin_role, role_read_modify_only, event_read_only_1, organisation, access_test_user_token, client
) -> None:
    request_body = {"info": "updated info"}
    event_id = event_read_only_1.id
    headers = {"authorization": access_test_user_token}
    response = client.put(f"events/{event_id}", json=request_body, headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_edit_existing_event_fail_read_only_user(event, read_only_user_token, client) -> None:
    request_body = {"info": "updated info"}
    event_id = event.id
    headers = {"authorization": read_only_user_token}
    response = client.put(f"events/{event_id}", json=request_body, headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_existing_event_read_only_user(
    role_read_modify_only, access_test_user, event_read_only_1, access_test_user_token, client
) -> None:
    event_id = event_read_only_1.id

    headers = {"authorization": access_test_user_token}
    response = client.delete(f"events/{event_id}", headers=headers)
    response_json = response.json()
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_existing_event_fail_read_only_user(
    role_read_modify_only, event, read_only_user_token, client
) -> None:
    event_id = event.id
    headers = {"authorization": read_only_user_token}
    response = client.delete(f"events/{event_id}", headers=headers)
    assert response.status_code == 403


# @pytest.mark.asyncio
# async def test_create_event(organisation, site_admin_user_token, client) -> None:
#    org_body = {
#        "id": organisation.id,
#        "name": organisation.name,
#        "uuid": organisation.uuid,
#        "local": organisation.local,
#    }
#
#    request_body = {
#        "info": "string",
#        "org_id": 0,
#        "distribution": 1,
#        "orgc_id": 0,
#        "org": org_body,
#        "org_c": org_body,
#        "uuid": "f1b356c7-777a-4f6b-8833-37e5525e9aaf",
#        "published": True,
#        "analysis": True,
#        "attribute_count": "string",
#        "timestamp": 0,
#        "sharing_group_id": 0,
#        "proposal_email_lock": True,
#        "locked": True,
#        "threat_level_id": 0,
#        "publish_timestamp": "string",
#        "sighting_timestamp": "string",
#        "disable_correlation": True,
#        "extends_uuid": "string",
#    }
#    headers = {"authorization": site_admin_user_token}
#    response = client.post("/events", json=request_body, headers=headers)
#    assert response.status_code == 200


# @pytest.mark.asyncio
# async def test_valid_freetext_import_readonly_user(organisation, event_read_only_1, attribute, access_test_user_token, client) -> None:
#     json = {"body": "json", "limit": 100}
#     headers = {"authorization": access_test_user_token}
#     eventid = event_read_only_1.id
#     response = client.post(f"/events/freeTextImport/{eventid}", json=json, headers=headers)
#     assert response.status_code == 200
#     response_json = response.json()
#     assert "response" in response_json
#     assert isinstance(response_json["response"], list)
#     print(len(response_json["response"]))
#     response_json_attribute = response_json["response"][0]
#     assert "Event" in response_json_attribute


@pytest.mark.asyncio
async def test_publish_existing_event_site_admin(
    event_read_only_1, event_read_only_2, site_admin_user_token, client
) -> None:
    event_id = event_read_only_2.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/events/publish/{event_id}", headers=headers)
    assert response.status_code == 200
