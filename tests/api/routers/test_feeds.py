from datetime import datetime
from time import time
from typing import Any, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from mmisp.db.models.event import Event
from mmisp.db.models.tag import Tag
from mmisp.tests.generators.feed_generator import (
    generate_random_valid_feed_data,
    generate_valid_feed_data,
    generate_valid_required_feed_data,
)


async def delete_feed(db, id):
    stmt = sa.sql.text("DELETE FROM feeds WHERE id=:id")
    await db.execute(stmt, {"id": id})
    await db.commit()


async def delete_event(db, id):
    stmt = sa.sql.text("DELETE FROM events WHERE id=:id")
    await db.execute(stmt, {"id": id})
    await db.commit()


@pytest.fixture(scope="module")
def feed_test_ids() -> Generator:
    yield {
        "non_existing_feed_id": "0",
        "invalid_feed_id": "invalid",
    }


@pytest.fixture(scope="module")
def cach_feed_test_data() -> Generator:
    yield {
        "valid_scope": "1",
        "invalid_scope": "0",
    }


@pytest.fixture(
    params=[
        generate_valid_required_feed_data().dict(),
        generate_valid_feed_data().dict(),
        generate_random_valid_feed_data().dict(),
        generate_random_valid_feed_data().dict(),
    ]
)
def feed_data(request: Any) -> dict[str, Any]:
    return request.param


@pytest_asyncio.fixture(autouse=True)
async def check_counts_stay_constant(db):
    count_sharing_groups = (await db.execute(text("SELECT COUNT(*) FROM sharing_groups"))).first()[0]
    count_sharing_groups_orgs = (await db.execute(text("SELECT COUNT(*) FROM sharing_group_orgs"))).first()[0]
    count_sharing_groups_servers = (await db.execute(text("SELECT COUNT(*) FROM sharing_group_servers"))).first()[0]
    yield
    ncount_sharing_groups = (await db.execute(text("SELECT COUNT(*) FROM sharing_groups"))).first()[0]
    ncount_sharing_groups_orgs = (await db.execute(text("SELECT COUNT(*) FROM sharing_group_orgs"))).first()[0]
    ncount_sharing_groups_servers = (await db.execute(text("SELECT COUNT(*) FROM sharing_group_servers"))).first()[0]

    assert count_sharing_groups == ncount_sharing_groups
    assert count_sharing_groups_orgs == ncount_sharing_groups_orgs
    assert count_sharing_groups_servers == ncount_sharing_groups_servers


@pytest.mark.asyncio
async def test_add_feed(
    feed_data: dict[str, Any],
    db: Session,
    instance_owner_org,
    instance_owner_org_admin_user,
    sharing_group,
    site_admin_user_token,
    client,
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id

    tag = Tag(
        name=str(time()) + uuid4().hex,
        colour="#FFFFFF",
        exportable=False,
        org_id=instance_owner_org.id,
        user_id=instance_owner_org_admin_user.id,
        local_only=True,
    )
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    feed_data["tag_id"] = tag.id

    event = Event(
        user_id=instance_owner_org_admin_user.id,
        org_id=instance_owner_org.id,
        orgc_id=instance_owner_org.id,
        info="test",
        date=datetime.utcnow(),
        analysis=0,
        sharing_group_id=feed_data["sharing_group_id"],
        threat_level_id=0,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    feed_data["event_id"] = event.id

    await db.commit()

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)

    assert response.status_code == 201
    assert response.json()["Feed"]["name"] == feed_data["name"]

    await db.delete(event)
    await db.commit()


@pytest.mark.asyncio
async def test_feed_error_handling(site_admin_user_token, client) -> None:
    invalid_data = {"name": "Test Feed"}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=invalid_data, headers=headers)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "field required"
    assert response.json()["detail"][0]["type"] == "value_error.missing"


@pytest.mark.asyncio
async def test_feed_response_format(
    feed_data: dict[str, Any],
    db: Session,
    site_admin_user_token,
    instance_owner_org,
    instance_owner_org_admin_user,
    sharing_group,
    event,
    client,
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id

    tag = Tag(
        name=str(time()) + uuid4().hex,
        colour="#FFFFFF",
        exportable=False,
        org_id=instance_owner_org.id,
        user_id=instance_owner_org_admin_user.id,
        local_only=True,
    )
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    feed_data["tag_id"] = tag.id

    feed_data["event_id"] = event.id
    await db.commit()

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    assert response.json()["Feed"]["name"] == feed_data["name"]
    assert response.json()["Feed"]["id"] is not None


@pytest.mark.asyncio
async def test_enable_feed(
    feed_test_ids: dict[str, Any], feed_data: dict[str, Any], sharing_group, tag, event, site_admin_user_token, client
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id
    feed_data["tag_id"] = tag.id
    feed_data["event_id"] = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)
    feed_id = response.json()["Feed"]["id"]
    assert response.status_code == 201

    response = client.post(f"feeds/enable/{feed_id}", headers=headers)
    assert response.status_code == 200

    response = client.post(f"feeds/enable/{feed_test_ids['non_existing_feed_id']}", headers=headers)
    assert response.status_code == 404

    response = client.post(f"feeds/enable/{feed_test_ids['invalid_feed_id']}", headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_feed_enable_response_format(
    feed_data: dict[str, Any], sharing_group, tag, event, site_admin_user_token, client
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id
    feed_data["tag_id"] = tag.id
    feed_data["event_id"] = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)
    feed_id = response.json()["Feed"]["id"]
    assert response.status_code == 201

    response = client.post(f"feeds/enable/{feed_id}", headers=headers)
    assert response.headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_disable_feed(
    feed_test_ids: dict[str, Any],
    feed_data: dict[str, Any],
    db: Session,
    sharing_group,
    tag,
    event,
    site_admin_user_token,
    client,
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id
    feed_data["tag_id"] = tag.id
    feed_data["event_id"] = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)
    feed_id = response.json()["Feed"]["id"]
    assert response.status_code == 201

    response = client.post(f"feeds/disable/{feed_id}", headers=headers)
    assert response.status_code == 200

    response = client.post(f"feeds/disable/{feed_test_ids['non_existing_feed_id']}", headers=headers)
    assert response.status_code == 404

    response = client.post(f"feeds/disable/{feed_test_ids['invalid_feed_id']}", headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_disable_feed_response_format(
    feed_data: dict[str, Any], db: Session, sharing_group, tag, event, site_admin_user_token, client
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id
    feed_data["tag_id"] = tag.id
    feed_data["event_id"] = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)
    feed_id = response.json()["Feed"]["id"]
    assert response.status_code == 201

    response = client.post(f"feeds/disable/{feed_id}", headers=headers)
    assert response.headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_get_existing_feed_details(
    feed_data: dict[str, Any], db: Session, sharing_group, tag, event, site_admin_user_token, client
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id
    feed_data["tag_id"] = tag.id
    feed_data["event_id"] = event.id

    await db.commit()

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)
    feed_id = response.json()["Feed"]["id"]
    assert response.status_code == 201

    response = client.get(f"/feeds/{feed_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["Feed"]["id"] == feed_id
    assert response.json()["Feed"]["name"] == feed_data["name"]


@pytest.mark.asyncio
async def test_get_invalid_feed_by_id(feed_test_ids: dict[str, Any], site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/feeds/{feed_test_ids['invalid_feed_id']}", headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_non_existing_feed_details(feed_test_ids: dict[str, Any], site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/feeds/{feed_test_ids['non_existing_feed_id']}", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_feed_response_format(
    feed_data: dict[str, Any], sharing_group, tag, event, site_admin_user_token, client
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id
    feed_data["tag_id"] = tag.id
    feed_data["event_id"] = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)
    feed_id = response.json()["Feed"]["id"]
    assert response.status_code == 201

    response = client.get(f"/feeds/{feed_id}", headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    data = response.json()
    assert "Feed" in data
    assert data["Feed"]["id"] == feed_id
    assert data["Feed"]["name"] == feed_data["name"]


@pytest.mark.asyncio
async def test_update_existing_feed(
    feed_data: dict[str, Any], sharing_group, tag, event, site_admin_user_token, client
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id
    feed_data["tag_id"] = tag.id
    feed_data["event_id"] = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)
    feed_id = response.json()["Feed"]["id"]
    assert response.status_code == 201

    headers = {"authorization": site_admin_user_token}
    response = client.put(f"/feeds/{feed_id}", json=feed_data, headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["Feed"]["name"] == feed_data["name"]
    assert response_data["Feed"]["url"] == feed_data["url"]


@pytest.mark.asyncio
async def test_update_non_existing_feed(
    feed_test_ids: dict[str, Any], feed_data: dict[str, Any], site_admin_user_token, client
) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.put(f"/feeds/{feed_test_ids['non_existing_feed_id']}", json=feed_data, headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_feed_response_format(
    feed_data: dict[str, Any], sharing_group, tag, event, site_admin_user_token, client
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id
    feed_data["tag_id"] = tag.id
    feed_data["event_id"] = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)
    feed_id = response.json()["Feed"]["id"]
    assert response.status_code == 201

    response = client.put(f"/feeds/{feed_id}", json=feed_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    assert "Feed" in response.json()
    assert response.json()["Feed"]["id"] == feed_id
    assert response.json()["Feed"]["name"] == feed_data["name"]


@pytest.mark.asyncio
async def test_toggle_existing_feed(
    feed_data: dict[str, Any], sharing_group, tag, event, site_admin_user_token, client
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id
    feed_data["tag_id"] = tag.id
    feed_data["event_id"] = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)
    feed_id = response.json()["Feed"]["id"]
    assert response.status_code == 201

    toggle_data = {"enable": False}
    response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
    assert response.status_code == 200

    toggle_data = {"enable": False}
    response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
    assert response.status_code == 200

    toggle_data = {"enable": True}
    response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
    assert response.status_code == 200

    toggle_data = {"enable": False}
    response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_toggle_non_existing_feed(feed_test_ids: dict[str, Any], site_admin_user_token, client) -> None:
    toggle_data = {"enable": True}
    headers = {"authorization": site_admin_user_token}
    response = client.patch(f"feeds/{feed_test_ids['non_existing_feed_id']}", json=toggle_data, headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_toggle_feed_response_format(
    feed_data: dict[str, Any], sharing_group, tag, event, site_admin_user_token, client
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id
    feed_data["tag_id"] = tag.id
    feed_data["event_id"] = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)
    feed_id = response.json()["Feed"]["id"]
    assert response.status_code == 201

    toggle_data = {"enable": True}
    response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    data = response.json()
    assert "name" in data
    assert data["message"] in ("Feed enabled successfully.", "Feed already enabled.")
    assert "url" in data

    toggle_data = {"enable": False}
    response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    data = response.json()
    assert "name" in data
    assert data["message"] == "Feed disabled successfully."
    assert "url" in data

    toggle_data = {"enable": False}
    response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    data = response.json()
    assert "name" in data
    assert data["message"] == "Feed already disabled."
    assert "url" in data

    toggle_data = {"enable": True}
    response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    data = response.json()
    assert "name" in data
    assert data["message"] == "Feed enabled successfully."
    assert "url" in data

    toggle_data = {"enable": True}
    response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    data = response.json()
    assert "name" in data
    assert data["message"] == "Feed already enabled."
    assert "url" in data


@pytest.mark.asyncio
async def test_get_all_feeds(
    feed_data: dict[str, Any], sharing_group, tag, event, site_admin_user_token, client
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id
    feed_data["tag_id"] = tag.id
    feed_data["event_id"] = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)
    assert response.status_code == 201

    response = client.get("/feeds", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_feeds_response_format(
    feed_data: dict[str, Any], sharing_group, tag, event, site_admin_user_token, client
) -> None:
    feed_data["sharing_group_id"] = sharing_group.id
    feed_data["tag_id"] = tag.id
    feed_data["event_id"] = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post("/feeds", json=feed_data, headers=headers)
    assert response.status_code == 201

    response = client.get("/feeds", headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    response_data = response.json()

    # Test all required fields
    assert "Feed" in response_data[0]
    for feed_wrapper in response_data:
        assert "id" in feed_wrapper["Feed"]
        assert "name" in feed_wrapper["Feed"]
        assert "provider" in feed_wrapper["Feed"]
        assert "url" in feed_wrapper["Feed"]
