import pytest
import respx
import sqlalchemy as sa
from httpx import Response
from icecream import ic

from mmisp.api.config import config
from mmisp.db.models.log import Log


@pytest.mark.asyncio
async def test_list_all_events_read_only_user(
    event, event5, event_read_only_1, organisation, access_test_user_token, client
) -> None:
    headers = {"authorization": access_test_user_token}
    response = client.get("/events", headers=headers)
    assert response.status_code == 200

    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 1


@pytest.mark.asyncio
async def test_list_all_events_admin(
    event3, event4, event5, organisation, event_read_only_1, site_admin_user_token, client
) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/events", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 4


@pytest.mark.asyncio
async def test_get_event_success_read_only_user(
    event_read_only_1, organisation, access_test_user, access_test_user_token, client
) -> None:
    headers = {"authorization": access_test_user_token}
    event_id = event_read_only_1.id
    print("Event ID: " + str(event_id))
    print("Event User ID: " + str(event_read_only_1.user_id))
    print("User ID: " + str(access_test_user.id))
    response = client.get(f"/events/{event_id}", headers=headers)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_event_fail_read_only_user(event, access_test_user_token, client) -> None:
    headers = {"authorization": access_test_user_token}
    event_id = event.id
    response = client.get(f"/events/{event_id}", headers=headers)

    assert response.status_code == 403
    response_json = response.json()
    assert response_json["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_get_event_success_site_admin(
    event_read_only_1, attribute_read_only_1, tag_read_only_1, site_admin_user_token, client
) -> None:
    headers = {"authorization": site_admin_user_token}
    event_id = event_read_only_1.id
    response = client.get(f"/events/{event_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    # assert "name" in response_json, f"'name' not found in response: {response_json}"
    assert response_json["Event"]["id"] == event_id


@pytest.mark.asyncio
async def test_valid_search_attribute_data_read_only_user(
    organisation, event_read_only_1, attribute_read_only_1, access_test_user_token, client
) -> None:
    json = {"returnFormat": "json", "limit": 100}
    headers = {"authorization": access_test_user_token}
    response = client.post("/events/restSearch", json=json, headers=headers)
    assert response.status_code == 200

    response_json = response.json()
    assert isinstance(response_json["response"], list)
    # assert len(response_json) == (less than with site_admin_user_token)


@pytest.mark.asyncio
async def test_publish_existing_event_read_only_user(
    role_read_modify_only, event_read_only_1, event_read_only_2, access_test_user_token, client
) -> None:
    event_id = event_read_only_2.id

    headers = {"authorization": access_test_user_token}
    response = client.post(f"/events/publish/{event_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_publish_existing_event_fail_read_only_user(event, access_test_user_token, client) -> None:
    event_id = event.id
    headers = {"authorization": access_test_user_token}
    response = client.post(f"/events/publish/{event_id}", headers=headers)
    response_json = response.json()
    assert response_json["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_add_existing_tag_to_event_read_only_user(event_read_only_1, tag, access_test_user_token, client) -> None:
    tag_id = tag.id
    event_id = event_read_only_1.id

    headers = {"authorization": access_test_user_token}
    response = client.post(f"/events/addTag/{event_id}/{tag_id}/local:1", headers=headers)
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["detail"] == "Success"


@pytest.mark.asyncio
async def test_add_existing_tag_to_event_fail_read_only_user(event, tag, access_test_user_token, client) -> None:
    tag_id = tag.id
    event_id = event.id

    headers = {"authorization": access_test_user_token}
    response = client.post(
        f"/events/addTag/{event_id}/{tag_id}/local:1",
        headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 403
    assert response_json["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_remove_existing_tag_from_event_read_only_user(
    event_read_only_1, tag, eventtag, access_test_user_token, client
) -> None:
    tag_id = tag.id
    event_id = event_read_only_1.id

    headers = {"authorization": access_test_user_token}
    response = client.post(f"/events/removeTag/{event_id}/{tag_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["success"] == "Success"


@pytest.mark.asyncio
async def test_remove_existing_tag_from_event_fail_read_only_user(
    event, tag, eventtag, access_test_user_token, client
) -> None:
    tag_id = tag.id
    event_id = event.id

    headers = {"authorization": access_test_user_token}
    response = client.post(f"/events/removeTag/{event_id}/{tag_id}", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_edit_existing_event_read_only_user(
    event_read_only_1, organisation, access_test_user_token, client
) -> None:
    request_body = {"info": "updated info"}
    event_id = event_read_only_1.id
    headers = {"authorization": access_test_user_token}
    response = client.put(f"events/{event_id}", json=request_body, headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["detail"] == "Success"


@pytest.mark.asyncio
async def test_edit_existing_event_fail_read_only_user(event, access_test_user_token, client) -> None:
    request_body = {"info": "updated info"}
    event_id = event.id
    headers = {"authorization": access_test_user_token}
    response = client.put(f"events/{event_id}", json=request_body, headers=headers)
    assert response.status_code == 403
    response_json = response.json()
    assert response_json["detail"] == "Forbidden"


@pytest.mark.asyncio
async def test_delete_existing_event_read_only_user(event_read_only_1, access_test_user_token, client) -> None:
    event_id = event_read_only_1.id

    headers = {"authorization": access_test_user_token}
    response = client.delete(f"events/{event_id}", headers=headers)
    response_json = response.json()
    print("Response: " + str(response_json))
    assert response.status_code == 200
    assert response_json["detail"]["name"] == "Success"


@pytest.mark.asyncio
async def test_delete_existing_event_fail_read_only_user(event, access_test_user_token, client) -> None:
    event_id = event.id

    headers = {"authorization": access_test_user_token}
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
