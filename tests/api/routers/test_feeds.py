from datetime import datetime
from time import time
from typing import Any, Generator
from uuid import uuid4

import pytest

from mmisp.db.models.event import Event
from mmisp.db.models.tag import Tag
from tests.environment import client, environment, get_db
from tests.generators.feed_generator import (
    generate_random_valid_feed_data,
    generate_valid_feed_data,
    generate_valid_required_feed_data,
)
from tests.generators.model_generators.sharing_group_generator import generate_sharing_group


@pytest.fixture(
    params=[
        generate_valid_required_feed_data().dict(),
        generate_valid_feed_data().dict(),
        generate_random_valid_feed_data().dict(),
        generate_random_valid_feed_data().dict(),
        generate_random_valid_feed_data().dict(),
    ]
)
def feed_data(request: Any) -> dict[str, Any]:
    return request.param


class TestAddFeed:
    @staticmethod
    def test_add_feed(feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)

        assert response.status_code == 201
        assert response.json()["feed"]["name"] == feed_data["name"]

    @staticmethod
    def test_feed_error_handling() -> None:
        invalid_data = {"name": "Test Feed"}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=invalid_data, headers=headers)
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "field required"
        assert response.json()["detail"][0]["type"] == "value_error.missing"

    @staticmethod
    def test_feed_response_format(feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        assert response.json()["feed"]["name"] == feed_data["name"]
        assert response.json()["feed"]["id"] is not None


@pytest.fixture(scope="module")
def feed_test_ids() -> Generator:
    yield {
        "non_existing_feed_id": "0",
        "invalid_feed_id": "invalid",
    }


class TestEnableFeed:
    @staticmethod
    def test_enable_feed(feed_test_ids: dict[str, Any], feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        response = client.post(f"feeds/enable/{feed_id}", headers=headers)
        assert response.status_code == 200

        response = client.post(f"feeds/enable/{feed_test_ids['non_existing_feed_id']}", headers=headers)
        assert response.status_code == 404

        response = client.post(f"feeds/enable/{feed_test_ids['invalid_feed_id']}", headers=headers)
        assert response.status_code == 422

    @staticmethod
    def test_feed_enable_response_format(feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        response = client.post(f"feeds/enable/{feed_id}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"


class TestDisableFeed:
    @staticmethod
    def test_disable_feed(feed_test_ids: dict[str, Any], feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        response = client.post(f"feeds/disable/{feed_id}", headers=headers)
        assert response.status_code == 200

        response = client.post(f"feeds/disable/{feed_test_ids['non_existing_feed_id']}", headers=headers)
        assert response.status_code == 404

        response = client.post(f"feeds/disable/{feed_test_ids['invalid_feed_id']}", headers=headers)
        assert response.status_code == 422

    @staticmethod
    def test_disable_feed_response_format(feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        response = client.post(f"feeds/disable/{feed_id}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"


@pytest.fixture(scope="module")
def cach_feed_test_data() -> Generator:
    yield {
        "valid_scope": "1",
        "invalid_scope": "0",
    }


class TestCacheFeeds:
    pass  # route not yet implemented (worker)

    # @staticmethod
    # def test_cache_feeds_valid_data(cach_feed_test_data: dict[str, Any]) -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.post(f"/feeds/cacheFeeds/{cach_feed_test_data['valid_scope']}", headers=headers)
    #     assert response.status_code == 200
    #     assert response.json()["success"] is True

    # @staticmethod
    # def test_cache_feeds_invalid_data(cach_feed_test_data: dict[str, Any]) -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.post(f"/feeds/cacheFeeds/{cach_feed_test_data['invalid_scope']}", headers=headers)
    #     assert response.status_code == 400

    # @staticmethod
    # def test_cache_feeds_response_format(cach_feed_test_data: dict[str, Any]) -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.post(f"/feeds/cacheFeeds/{cach_feed_test_data['valid_scope']}", headers=headers)
    #     assert response.headers["Content-Type"] == "application/json"


class TestFetchFeeds:
    pass  # route not yet implemented (worker)

    # @staticmethod
    # def test_fetch_from_feed_existing_id(feed_test_ids: dict[str, Any]) -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.get(f"/feeds/fetchFromFeed/{feed_test_ids['valid_feed_id']}", headers=headers)
    #     assert response.status_code == 200
    #     assert "result" in response.json()

    # @staticmethod
    # def test_fetch_from_feed_invalid_id(feed_test_ids: dict[str, Any]) -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.get(f"/feeds/fetchFromFeed/{feed_test_ids['invalid_feed_id']}", headers=headers)
    #     assert response.status_code == 422

    # @staticmethod
    # def test_fetch_from_feed_non_existing_id(feed_test_ids: dict[str, Any]) -> None:
    #     response = client.get(f"/feeds/fetchFromFeed/{feed_test_ids['non_existing_feed_id']}")
    #     assert response.status_code in (404, 405)

    # @staticmethod
    # def test_fetch_from_feed_response_format(feed_test_ids: dict[str, Any]) -> None:
    #     response = client.get(f"/feeds/fetchFromFeed/{feed_test_ids['valid_feed_id']}")
    #     assert response.headers["Content-Type"] == "application/json"


class TestGetFeedByIdInfo:
    @staticmethod
    def test_get_existing_feed_details(feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        response = client.get(f"/feeds/{feed_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["feed"]["id"] == feed_id
        assert response.json()["feed"]["name"] == feed_data["name"]

    @staticmethod
    def test_get_invalid_feed_by_id(feed_test_ids: dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/feeds/{feed_test_ids['invalid_feed_id']}", headers=headers)
        assert response.status_code == 422

    @staticmethod
    def test_get_non_existing_feed_details(feed_test_ids: dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/feeds/{feed_test_ids['non_existing_feed_id']}", headers=headers)
        assert response.status_code == 404

    @staticmethod
    def test_get_feed_response_format(feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        response = client.get(f"/feeds/{feed_id}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        data = response.json()
        assert "feed" in data
        assert data["feed"]["id"] == feed_id
        assert data["feed"]["name"] == feed_data["name"]


class TestUpdateFeed:
    @staticmethod
    def test_update_existing_feed(feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        headers = {"authorization": environment.site_admin_user_token}
        response = client.put(f"/feeds/{feed_id}", json=feed_data, headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["feed"]["name"] == feed_data["name"]
        assert response_data["feed"]["url"] == feed_data["url"]

    @staticmethod
    def test_update_non_existing_feed(feed_test_ids: dict[str, Any], feed_data: dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.put(f"/feeds/{feed_test_ids['non_existing_feed_id']}", json=feed_data, headers=headers)
        assert response.status_code == 404

    @staticmethod
    def test_update_feed_response_format(feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        headers = {"authorization": environment.site_admin_user_token}
        response = client.put(f"/feeds/{feed_id}", json=feed_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        assert "feed" in response.json()
        assert response.json()["feed"]["id"] == feed_id
        assert response.json()["feed"]["name"] == feed_data["name"]


class TestToggleFeed:
    @staticmethod
    def test_toggle_existing_feed(feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        toggle_data = {"enable": False}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
        assert response.status_code == 200

        toggle_data = {"enable": False}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
        assert response.status_code == 200

        toggle_data = {"enable": True}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
        assert response.status_code == 200

        toggle_data = {"enable": False}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
        assert response.status_code == 200

    @staticmethod
    def test_toggle_non_existing_feed(feed_test_ids: dict[str, Any]) -> None:
        toggle_data = {"enable": True}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.patch(f"feeds/{feed_test_ids['non_existing_feed_id']}", json=toggle_data, headers=headers)
        assert response.status_code == 404

    @staticmethod
    def test_toggle_feed_response_format(feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        toggle_data = {"enable": True}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        data = response.json()
        assert "name" in data
        assert data["message"] in ("Feed enabled successfully.", "Feed already enabled.")
        assert "url" in data

        toggle_data = {"enable": False}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        data = response.json()
        assert "name" in data
        assert data["message"] == "Feed disabled successfully."
        assert "url" in data

        toggle_data = {"enable": False}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        data = response.json()
        assert "name" in data
        assert data["message"] == "Feed already disabled."
        assert "url" in data

        toggle_data = {"enable": True}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        data = response.json()
        assert "name" in data
        assert data["message"] == "Feed enabled successfully."
        assert "url" in data

        toggle_data = {"enable": True}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        data = response.json()
        assert "name" in data
        assert data["message"] == "Feed already enabled."
        assert "url" in data


class TestFetschFromAllFeeds:
    pass  # route not yet implemented (worker)

    # @staticmethod
    # def test_fetch_data_from_all_feeds() -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.get("/feeds/fetchFromAllFeeds", headers=headers)
    #     assert response.status_code == 200
    #     response_data = response.json()
    #     assert "result" in response_data

    # @staticmethod
    # def test_fetch_from_all_feeds_response_format() -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.get("/feeds/fetchFromAllFeeds", headers=headers)
    #     assert response.headers["Content-Type"] == "application/json"
    #     assert "result" in response.json()


class TestGetAllFeeds:
    @staticmethod
    def test_get_all_feeds(feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        assert response.status_code == 201

        response = client.get("/feeds", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json()["feeds"], list)

    @staticmethod
    def test_get_feeds_response_format(feed_data: dict[str, Any]) -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id
        db.add(sharing_group)
        db.flush()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name=str(time()) + uuid4().hex,
            colour="#FFFFFF",
            exportable=False,
            org_id=environment.instance_owner_org.id,
            user_id=environment.instance_owner_org_admin_user.id,
        )
        db.add(tag)
        db.flush()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(
            org_id=environment.instance_owner_org.id,
            orgc_id=environment.instance_owner_org.id,
            info="test",
            date=datetime.utcnow(),
            analysis="test",
            event_creator_email=generate_unique_email(),
        )
        db.add(event)
        db.flush()
        db.refresh(event)
        feed_data["event_id"] = event.id

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        assert response.status_code == 201

        response = client.get("/feeds", headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        response_data = response.json()
        assert isinstance(response_data["feeds"], list)

        # Test all required fields
        assert "feeds" in response_data
        for feed_wrapper in response_data["feeds"]:
            assert "id" in feed_wrapper
            assert "name" in feed_wrapper
            assert "provider" in feed_wrapper
            assert "url" in feed_wrapper


def generate_unique_email() -> str:
    timestamp = int(time())
    random_str = uuid4().hex
    email = f"unique-{timestamp}-{random_str}@test"
    return email
