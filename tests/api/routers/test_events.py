import sqlalchemy as sa

from mmisp.db.models.log import Log


def delete_event(db, id):
    stmt = sa.sql.text("DELETE FROM events WHERE id=:id")
    db.execute(stmt, {"id": id})
    db.commit()


def test_add_event_valid_data(db, site_admin_user_token, client) -> None:
    request_body = {"info": "test event"}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Event"]["info"] == request_body["info"]
    assert "id" in response_json["Event"]["Org"]
    assert "name" in response_json["Event"]["Org"]
    assert "uuid" in response_json["Event"]["Org"]
    assert "local" in response_json["Event"]["Org"]

    delete_event(db, response_json["Event"]["id"])


def test_add_event_date_empty_string(db, site_admin_user_token, client) -> None:
    request_body = {"info": "test event", "date": ""}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Event"]["info"] == request_body["info"]
    assert "id" in response_json["Event"]["Org"]
    assert "name" in response_json["Event"]["Org"]
    assert "uuid" in response_json["Event"]["Org"]
    assert "local" in response_json["Event"]["Org"]

    delete_event(db, response_json["Event"]["id"])


def test_get_existing_event(
    organisation, event, attribute, galaxy, galaxy_cluster, tag, site_admin_user_token, eventtag, client
) -> None:
    org_id = organisation.id

    event_id = event.id
    attribute_id = attribute.id
    galaxy_id = galaxy.id
    tag_id = tag.id

    galaxy_cluster_id = galaxy_cluster.id

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/events/{event_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Event"]["id"] == str(event_id)
    assert response_json["Event"]["org_id"] == str(org_id)
    assert response_json["Event"]["orgc_id"] == str(org_id)
    assert response_json["Event"]["attribute_count"] == "1"
    assert response_json["Event"]["Attribute"][0]["id"] == str(attribute_id)
    assert response_json["Event"]["Tag"][0]["id"] == str(tag_id)
    assert response_json["Event"]["Galaxy"][0]["id"] == str(galaxy_id)
    assert response_json["Event"]["Galaxy"][0]["GalaxyCluster"][0]["id"] == str(galaxy_cluster_id)
    assert response_json["Event"]["Galaxy"][0]["GalaxyCluster"][0]["event_tag_id"] == str(eventtag.id)


def test_get_non_existing_event(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/events/0", headers=headers)
    assert response.status_code == 404
    response = client.get("/events/invalid_id", headers=headers)
    assert response.status_code == 404


def test_update_existing_event(event, site_admin_user_token, client) -> None:
    request_body = {"info": "updated info"}
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.put(f"events/{event_id}", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Event"]["info"] == request_body["info"]


def test_update_non_existing_event(site_admin_user_token, client) -> None:
    request_body = {"info": "updated event"}
    headers = {"authorization": site_admin_user_token}
    response = client.put("/events/0", json=request_body, headers=headers)
    assert response.status_code == 404

    response = client.put("/events/invalid_id", json=request_body, headers=headers)
    assert response.status_code == 404


def test_delete_existing_event(event, site_admin_user_token, client) -> None:
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"events/{event_id}", headers=headers)

    assert response.status_code == 200


def test_delete_invalid_or_non_existing_event(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete("/events/0", headers=headers)
    assert response.status_code == 404
    response = client.delete("/events/invalid_id", headers=headers)
    assert response.status_code == 404


def test_get_all_events(event, event2, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/events", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)


def test_valid_search_attribute_data(organisation, event, attribute, site_admin_user_token, client) -> None:
    json = {"returnFormat": "json", "limit": 100}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events/restSearch", json=json, headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert "response" in response_json
    assert isinstance(response_json["response"], list)
    response_json_attribute = response_json["response"][0]
    assert "Event" in response_json_attribute


def test_invalid_search_attribute_data(site_admin_user_token, client) -> None:
    json = {"returnFormat": "invalid format"}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events/restSearch", json=json, headers=headers)
    assert response.status_code == 404


def test_index_events_valid_data(organisation, event, site_admin_user_token, client) -> None:
    json = {"distribution": "1"}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events/index", json=json, headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert "id" in response_json[0]
    assert "GalaxyCluster" in response_json[0]


def test_publish_existing_event(organisation, event, site_admin_user_token, client) -> None:
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
    assert response_json["id"] == str(event_id)


def test_publish_existing_event_workflow_blocked(
    organisation, event, site_admin_user_token, client, blocking_publish_workflow, db
) -> None:
    event_id = event.id

    # Ensure clean slate, other tests also log and there's
    # no centralized cleaning up for that so far.
    db.execute(sa.delete(Log))
    db.commit()

    assert len(db.execute(sa.select(Log).where(Log.model == "Workflow")).scalars().all()) == 0

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/events/publish/{event_id}", headers=headers)

    assert response.status_code == 400
    assert response.json() == {
        "message": (
            "Workflow 'event-publish' is blocking and failed with the following errors:\n"
            "Stopped publish of test event"
        )
    }

    db.refresh(event)
    assert not event.published

    assert len(db.execute(sa.select(Log).where(Log.model == "Workflow")).scalars().all()) == 3
    assert db.execute(sa.select(Log.title).where(Log.model == "Workflow")).scalars().all() == [
        "Started executing workflow for trigger `Event Publish` (1)",
        (
            "Executed node `stop-execution`\nNode `stop-execution` from Workflow `Demo workflow` "
            "(1) executed successfully with status: partial-success"
        ),
        "Finished executing workflow for trigger `Event Publish` (1). Outcome: blocked",
    ]

    db.execute(sa.delete(Log))
    db.commit()


def test_unsupported_module_breaks_publish(
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

    db.refresh(event)
    assert not event.published
    assert len(db.execute(sa.select(Log).where(Log.model == "Workflow")).scalars().all()) == 1
    assert db.execute(sa.select(Log.title).where(Log.model == "Workflow")).scalars().all() == [
        "Workflow was not executed, because it contained unsupported modules with the following IDs: demo"
    ]
    db.execute(sa.delete(Log))
    db.commit()


def test_publish_invalid_event(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events/publish/0", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "Invalid event."
    assert response_json["message"] == "Invalid event."
    assert response_json["url"] == "/events/publish/0"
    response = client.post("/events/publish/invalid_id", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "Invalid event."
    assert response_json["message"] == "Invalid event."
    assert response_json["url"] == "/events/publish/invalid_id"


def test_publish_existing_event2(event, site_admin_user_token, client) -> None:
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
    assert response_json["id"] == str(event_id)


def test_publish_invalid_event2(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events/unpublish/0", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "Invalid event."
    assert response_json["message"] == "Invalid event."
    assert response_json["url"] == "/events/unpublish/0"
    response = client.post("/events/unpublish/invalid_id", headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "Invalid event."
    assert response_json["message"] == "Invalid event."
    assert response_json["url"] == "/events/unpublish/invalid_id"


def test_add_existing_tag_to_attribute(event, tag, site_admin_user_token, client) -> None:
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


def test_add_invalid_or_non_existing_tag_to_attribute(event, site_admin_user_token, client) -> None:
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


def test_remove_existing_tag_from_attribute(event, tag, eventtag, site_admin_user_token, client) -> None:
    tag_id = tag.id
    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/events/removeTag/{event_id}/{tag_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["success"] == "Tag removed"
