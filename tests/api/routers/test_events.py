import uuid

import pytest
import respx
import sqlalchemy as sa
from httpx import Response
from icecream import ic

from mmisp.api.config import config
from mmisp.db.models.log import Log


@respx.mock
@pytest.mark.asyncio
async def test_freetext_import_stub(client, site_admin_user_token):
    response = client.post(
        "/events/freeTextImport/123",
        json={"value": "I spilled my coffee fuuuuu", "returnMetaAttributes": False},
        headers={"Authorization": site_admin_user_token},
    )
    assert response.status_code == 501
    assert response.json() == {"detail": "returnMetaAttributes = false is not implemented"}


@respx.mock
@pytest.mark.asyncio
async def test_freetext_import(client, site_admin_user_token):
    respx.post(f"{config.WORKER_URL}/job/processFreeText").mock(return_value=Response(200, json={"job_id": "777"}))

    response = client.post(
        "/events/freeTextImport/123",
        json={"value": "security leak at website.com", "returnMetaAttributes": True},
        headers={"Authorization": site_admin_user_token},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/jobs/processFreeText/777"


async def get_max_event_id(db):
    stmt = sa.sql.text("SELECT max(id) FROM events")
    result = await db.execute(stmt)

    result = result.scalar()
    if result is None:
        return 0
    return result


async def delete_event(db, id):
    stmt = sa.sql.text("DELETE FROM events WHERE id=:id")
    result = await db.execute(stmt, {"id": id})
    await db.commit()
    assert result.rowcount == 1


@pytest.mark.asyncio
async def test_add_event_valid_data(db, site_admin_user_token, client) -> None:
    request_body = {"info": "test event"}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Event"]["info"] == request_body["info"]
    assert "id" in response_json["Event"]["Org"]
    assert "name" in response_json["Event"]["Org"]
    assert uuid.UUID(response_json["Event"]["Org"]["uuid"])
    assert uuid.UUID(response_json["Event"]["Orgc"]["uuid"])
    assert "local" in response_json["Event"]["Org"]
    assert uuid.UUID(response_json["Event"]["uuid"])

    await delete_event(db, response_json["Event"]["id"])


@pytest.mark.asyncio
async def test_add_event_date_empty_string(db, site_admin_user_token, client) -> None:
    request_body = {"info": "test event", "date": ""}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Event"]["info"] == request_body["info"]
    assert "id" in response_json["Event"]["Org"]
    assert "name" in response_json["Event"]["Org"]
    assert uuid.UUID(response_json["Event"]["Org"]["uuid"])
    assert uuid.UUID(response_json["Event"]["Orgc"]["uuid"])
    assert "local" in response_json["Event"]["Org"]
    assert uuid.UUID(response_json["Event"]["uuid"])

    await delete_event(db, response_json["Event"]["id"])


@pytest.mark.asyncio
async def test_get_existing_event(
    organisation, event, attribute, galaxy, galaxy_cluster, tag, site_admin_user_token, eventtag, client
) -> None:
    ic("test")
    org_id = organisation.id

    event_id = event.id
    attribute_id = attribute.id
    galaxy_id = galaxy.id
    tag_id = tag.id

    galaxy_cluster_id = galaxy_cluster.id

    headers = {"authorization": site_admin_user_token}
    ic("event_id", event_id)

    response = client.get(f"/events/{event_id}", headers=headers)
    ic("response", response)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Event"]["id"] == event_id
    assert response_json["Event"]["org_id"] == org_id
    assert response_json["Event"]["orgc_id"] == org_id
    assert response_json["Event"]["attribute_count"] == 1
    assert response_json["Event"]["Attribute"][0]["id"] == attribute_id
    assert response_json["Event"]["Tag"][0]["id"] == tag_id
    assert response_json["Event"]["Galaxy"][0]["id"] == galaxy_id
    assert response_json["Event"]["Galaxy"][0]["GalaxyCluster"][0]["id"] == galaxy_cluster_id
    assert response_json["Event"]["Galaxy"][0]["GalaxyCluster"][0]["event_tag_id"] == eventtag.id


@pytest.mark.asyncio
async def test_get_event_sharing_group(event_unpublished_sharing_group, site_admin_user_token, client) -> None:
    event = event_unpublished_sharing_group
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    ic("event_id", event_id)

    response = client.get(f"/events/{event_id}", headers=headers)
    ic("response", response)

    assert response.status_code == 200
    response_json = response.json()
    ic(response_json)
    assert "SharingGroup" in response_json["Event"]
    assert "organisation_uuid" in response_json["Event"]["SharingGroup"]
    assert "Organisation" in response_json["Event"]["SharingGroup"]
    assert "SharingGroupOrg" in response_json["Event"]["SharingGroup"]
    assert "Organisation" in response_json["Event"]["SharingGroup"]["SharingGroupOrg"][0]
    assert "SharingGroupServer" in response_json["Event"]["SharingGroup"]


@pytest.mark.asyncio
async def test_get_existing_event_by_uuid(
    organisation, event, attribute, galaxy, galaxy_cluster, tag, site_admin_user_token, eventtag, client
) -> None:
    ic("test")
    org_id = organisation.id

    event_id = event.id
    event_uuid = event.uuid
    attribute_id = attribute.id
    galaxy_id = galaxy.id
    tag_id = tag.id

    galaxy_cluster_id = galaxy_cluster.id

    headers = {"authorization": site_admin_user_token}
    ic("event_id", event_id)

    response = client.get(f"/events/{event_uuid}", headers=headers)
    ic("response", response)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Event"]["id"] == event_id
    assert response_json["Event"]["uuid"] == str(event_uuid)
    assert response_json["Event"]["org_id"] == org_id
    assert response_json["Event"]["orgc_id"] == org_id
    assert response_json["Event"]["attribute_count"] == 1
    assert response_json["Event"]["Attribute"][0]["id"] == attribute_id
    assert response_json["Event"]["Tag"][0]["id"] == tag_id
    assert response_json["Event"]["Galaxy"][0]["id"] == galaxy_id
    assert response_json["Event"]["Galaxy"][0]["GalaxyCluster"][0]["id"] == galaxy_cluster_id
    assert response_json["Event"]["Galaxy"][0]["GalaxyCluster"][0]["event_tag_id"] == eventtag.id


@pytest.mark.asyncio
async def test_get_non_existing_event(db, site_admin_user_token, client) -> None:
    unused_event_id = await get_max_event_id(db) + 1
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/events/{unused_event_id}", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_non_existing_event_by_uuid(db, site_admin_user_token, client) -> None:
    unused_event_id = "a469325efe2f4f32a6854579f415ec6a"  # just a random, valid uuid. Extremely unlikely,
    headers = {"authorization": site_admin_user_token}  # that this one is already used in the db
    response = client.get(f"/events/{unused_event_id}", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_existing_event(event, site_admin_user_token, client) -> None:
    request_body = {"info": "updated info"}
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.put(f"events/{event_id}", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Event"]["info"] == request_body["info"]


@pytest.mark.asyncio
async def test_update_existing_event_by_uuid(event, site_admin_user_token, client) -> None:
    request_body = {"info": "updated info"}
    event_uuid = event.uuid

    headers = {"authorization": site_admin_user_token}
    response = client.put(f"events/{event_uuid}", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Event"]["info"] == request_body["info"]


@pytest.mark.asyncio
async def test_update_existing_event_has_rolled_back_transaction(
    event, site_admin_user_token, client, failing_before_save_workflow, db
) -> None:
    request_body = {"info": "updated info"}
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.put(f"events/{event_id}", json=request_body, headers=headers)

    assert response.status_code == 400
    await db.refresh(event)
    assert event.info == "test event"
    assert len((await db.execute(sa.select(Log).where(Log.model == "Workflow"))).scalars().all()) == 3
    assert (await db.execute(sa.select(Log.title).where(Log.model == "Workflow"))).scalars().all() == [
        "Started executing workflow for trigger `Event Before Save` (1)",
        "Executed node `stop-execution`\n"
        "Node `stop-execution` from Workflow `Before save workflow` (1) executed "
        "successfully with status: partial-success",
        "Finished executing workflow for trigger `Event Before Save` (1). Outcome: blocked",
    ]
    await db.execute(sa.delete(Log))
    await db.commit()


@pytest.mark.asyncio
async def test_update_non_existing_event(site_admin_user_token, client) -> None:
    request_body = {"info": "updated event"}
    headers = {"authorization": site_admin_user_token}
    response = client.put("/events/0", json=request_body, headers=headers)
    assert response.status_code == 404

    # Test random UUID
    response = client.put("/events/a469325efe2f4f32a6854579f415ec6a", json=request_body, headers=headers)
    assert response.status_code == 404

    response = client.put("/events/invalid_id", json=request_body, headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_existing_event(event, site_admin_user_token, client) -> None:
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"events/{event_id}", headers=headers)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_existing_event_by_uuid(event, site_admin_user_token, client) -> None:
    event_uuid = event.uuid
    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"events/{event_uuid}", headers=headers)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_invalid_or_non_existing_event(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete("/events/0", headers=headers)
    assert response.status_code == 404

    response = client.delete("/events/a469325efe2f4f32a6854579f415ec6a", headers=headers)
    assert response.status_code == 404

    response = client.delete("/events/invalid_id", headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_all_events(event, event2, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/events", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)


@pytest.mark.asyncio
async def test_valid_search_attribute_data(organisation, event, attribute, site_admin_user_token, client) -> None:
    json = {"returnFormat": "json", "limit": 100}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events/restSearch", json=json, headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert "response" in response_json
    assert isinstance(response_json["response"], list)
    response_json_attribute = response_json["response"][0]
    assert "Event" in response_json_attribute


@pytest.mark.asyncio
async def test_invalid_search_attribute_data(site_admin_user_token, client) -> None:
    json = {"returnFormat": "invalid format"}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events/restSearch", json=json, headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_index_events_valid_data(organisation, event, site_admin_user_token, client) -> None:
    json = {"distribution": 1}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events/index", json=json, headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert "id" in response_json[0]
    assert "GalaxyCluster" in response_json[0]


@pytest.mark.asyncio
async def test_publish_existing_event(organisation, event, site_admin_user_token, client) -> None:
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/events/publish/{event_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["saved"]
    assert response_json["success"]
    assert response_json["name"] == "Job queued"
    assert response_json["message"] == "Job queued"
    assert response_json["url"] == f"/events/publish/{event_id}"
    assert response_json["id"] == event_id


@pytest.mark.asyncio
async def test_publish_existing_event_by_uuid(organisation, event, site_admin_user_token, client) -> None:
    event_uuid = event.uuid

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/events/publish/{event_uuid}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["saved"]
    assert response_json["success"]
    assert response_json["name"] == "Job queued"
    assert response_json["message"] == "Job queued"
    assert response_json["url"] == f"/events/publish/{event_uuid}"
    assert response_json["id"] == str(event_uuid)


@pytest.mark.asyncio
async def test_publish_existing_event_workflow_blocked(
    organisation, event, site_admin_user_token, client, blocking_publish_workflow, db
) -> None:
    event_id = event.id

    # Ensure clean slate, other tests also log and there's
    # no centralized cleaning up for that so far.
    await db.execute(sa.delete(Log))
    await db.commit()

    assert len((await db.execute(sa.select(Log).where(Log.model == "Workflow"))).scalars().all()) == 0

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/events/publish/{event_id}", headers=headers)

    assert response.status_code == 400
    assert response.json() == {
        "message": (
            "Workflow 'event-publish' is blocking and failed with the following errors:\nStopped publish of test event"
        )
    }

    await db.refresh(event)
    assert not event.published

    # Terminate transaction to get new DB state.
    await db.commit()

    assert len((await db.execute(sa.select(Log).where(Log.model == "Workflow"))).scalars().all()) == 3
    assert (await db.execute(sa.select(Log.title).where(Log.model == "Workflow"))).scalars().all() == [
        "Started executing workflow for trigger `Event Publish` (1)",
        (
            "Executed node `stop-execution`\nNode `stop-execution` from Workflow `Demo workflow` "
            "(1) executed successfully with status: partial-success"
        ),
        "Finished executing workflow for trigger `Event Publish` (1). Outcome: blocked",
    ]

    await db.execute(sa.delete(Log))
    await db.commit()


@pytest.mark.asyncio
async def test_unsupported_module_breaks_publish(
    organisation, event, site_admin_user_token, client, unsupported_workflow, db
):
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/events/publish/{event_id}", headers=headers)

    assert response.status_code == 400
    assert response.json() == {
        "message": (
            "Workflow 'event-publish' is blocking and failed with the following errors:\n"
            "Workflow could not be executed, because it contains unsupported modules with the following IDs: demo"
        )
    }

    await db.refresh(event)
    assert not event.published
    # Terminate transaction to get new DB state.
    await db.commit()
    assert len((await db.execute(sa.select(Log).where(Log.model == "Workflow"))).scalars().all()) == 1
    assert (await db.execute(sa.select(Log.title).where(Log.model == "Workflow"))).scalars().all() == [
        "Workflow was not executed, because it contained unsupported modules with the following IDs: demo"
    ]
    await db.execute(sa.delete(Log))
    await db.commit()


@pytest.mark.asyncio
async def test_publish_invalid_event(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events/publish/0", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "You do not have the permission to do that."
    assert response_json["message"] == "You do not have the permission to do that."
    assert response_json["url"] == "/events/publish/0"

    response = client.post("/events/publish/999999999", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "You do not have the permission to do that."
    assert response_json["message"] == "You do not have the permission to do that."
    assert response_json["url"] == "/events/publish/999999999"

    response = client.post("/events/publish/a469325efe2f4f32a6854579f415ec6a", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "You do not have the permission to do that."
    assert response_json["message"] == "You do not have the permission to do that."
    assert response_json["url"] == "/events/publish/a469325efe2f4f32a6854579f415ec6a"


@pytest.mark.asyncio
async def test_unpublish_existing_event(event, site_admin_user_token, client) -> None:
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/events/unpublish/{event_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["saved"]
    assert response_json["success"]
    assert response_json["name"] == "Event unpublished."
    assert response_json["message"] == "Event unpublished."
    assert response_json["url"] == f"/events/unpublish/{event_id}"
    assert response_json["id"] == event_id


@pytest.mark.asyncio
async def test_unpublish_existing_event_by_uuid(event, site_admin_user_token, client) -> None:
    event_uuid = event.uuid

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/events/unpublish/{event_uuid}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["saved"]
    assert response_json["success"]
    assert response_json["name"] == "Event unpublished."
    assert response_json["message"] == "Event unpublished."
    assert response_json["url"] == f"/events/unpublish/{event_uuid}"
    assert response_json["id"] == str(event_uuid)


@pytest.mark.asyncio
async def test_unpublish_invalid_event(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    response = client.post("/events/unpublish/0", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "Invalid event."
    assert response_json["message"] == "Invalid event."
    assert response_json["url"] == "/events/unpublish/0"

    response = client.post("/events/unpublish/999999999", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "Invalid event."
    assert response_json["message"] == "Invalid event."
    assert response_json["url"] == "/events/unpublish/999999999"

    response = client.post("/events/unpublish/a469325efe2f4f32a6854579f415ec6a", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "Invalid event."
    assert response_json["message"] == "Invalid event."
    assert response_json["url"] == "/events/unpublish/a469325efe2f4f32a6854579f415ec6a"


@pytest.mark.asyncio
async def test_add_existing_tag_to_event(event, tag, site_admin_user_token, client) -> None:
    tag_id = tag.id
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(
        f"/events/addTag/{event_id}/{tag_id}/local:1",
        headers=headers,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["success"] == "Tag added"
    assert response_json["check_publish"]


@pytest.mark.asyncio
async def test_add_existing_tag_to_event_by_uuid(event, tag, site_admin_user_token, client) -> None:
    tag_id = tag.id
    event_uuid = event.uuid

    headers = {"authorization": site_admin_user_token}
    response = client.post(
        f"/events/addTag/{event_uuid}/{tag_id}/local:1",
        headers=headers,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["success"] == "Tag added"
    assert response_json["check_publish"]


@pytest.mark.asyncio
async def test_add_invalid_or_non_existing_tag_to_event(event, site_admin_user_token, client) -> None:
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(
        f"/events/addTag/{event_id}/0/local:1",
        headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"] is False
    response = client.post(
        f"/events/addTag/{event_id}/invalid_id/local:1",
        headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"] is False


@pytest.mark.asyncio
async def test_remove_existing_tag_from_event(event, tag, eventtag, site_admin_user_token, client) -> None:
    tag_id = tag.id
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/events/removeTag/{event_id}/{tag_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["success"] == "Tag removed"


@pytest.mark.asyncio
async def test_remove_existing_tag_from_event_by_uuid(event, tag, eventtag, site_admin_user_token, client) -> None:
    tag_id = tag.id
    event_uuid = event.uuid

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/events/removeTag/{event_uuid}/{tag_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["success"] == "Tag removed"
