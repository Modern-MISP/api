import random
import string
from typing import Any, Dict, Generator

import pytest

from mmisp.db.models.event import Event
from mmisp.db.models.sharing_group import SharingGroup
from mmisp.db.models.tag import Tag

from ...environment import client, environment, get_db
from ...generators.feed_generator import (
    generate_random_valid_feed_data,
    generate_valid_feed_data,
    generate_valid_required_feed_data,
)


@pytest.fixture(
    params=[
        generate_valid_required_feed_data().dict(),
        generate_valid_feed_data().dict(),
        generate_random_valid_feed_data().dict(),
        generate_random_valid_feed_data().dict(),
        generate_random_valid_feed_data().dict(),
    ]
)
def feed_data(request: Any) -> Dict[str, Any]:
    return request.param


class TestAddFeed:
    def test_add_feed(self: "TestAddFeed", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)

        assert response.status_code == 201
        assert response.json()["feed"]["name"] == feed_data["name"]

    def test_feed_error_handling(self: "TestAddFeed") -> None:
        invalid_data = {"name": "Test Feed"}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=invalid_data, headers=headers)
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "field required"
        assert response.json()["detail"][0]["type"] == "value_error.missing"

    def test_feed_response_format(self: "TestAddFeed", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        assert response.json()["feed"]["name"] == feed_data["name"]
        assert response.json()["feed"]["id"] is not None

    def test_add_feed_authorization(self: "TestAddFeed", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": ""}
        response = client.post("/feeds", json=feed_data, headers=headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"
        assert response.headers["Content-Type"] == "application/json"


@pytest.fixture(scope="module")
def feed_test_ids() -> Generator:
    yield {
        "non_existing_feed_id": "0",
        "invalid_feed_id": "invalid",
    }


class TestEnableFeed:
    def test_enable_feed(self: "TestEnableFeed", feed_test_ids: Dict[str, Any], feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        response = client.post(f"feeds/enable/{feed_id}", headers=headers)
        assert response.status_code == 200

        response = client.post(f"feeds/enable/{feed_test_ids['non_existing_feed_id']}", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Feed not found."

        response = client.post(f"feeds/enable/{feed_test_ids['invalid_feed_id']}", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Feed not found."

    def test_feed_enable_response_format(self: "TestEnableFeed", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        response = client.post(f"feeds/enable/{feed_id}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"

    def test_enable_feed_authorization(self: "TestEnableFeed", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        headers = {"authorization": ""}
        response = client.post(f"feeds/enable/{feed_id}", headers=headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"


class TestDisableFeed:
    def test_disable_feed(self: "TestDisableFeed", feed_test_ids: Dict[str, Any], feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        response = client.post(f"feeds/disable/{feed_id}", headers=headers)
        assert response.status_code == 200

        response = client.post(f"feeds/disable/{feed_test_ids['non_existing_feed_id']}", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Feed not found."

        response = client.post(f"feeds/disable/{feed_test_ids['invalid_feed_id']}", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Feed not found."

    def test_disable_feed_response_format(self: "TestDisableFeed", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        response = client.post(f"feeds/disable/{feed_id}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"

    def test_disable_feed_authorization(self: "TestDisableFeed", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        headers = {"authorization": ""}
        response = client.post(f"feeds/enable/{feed_id}", headers=headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"


@pytest.fixture(scope="module")
def cach_feed_test_data() -> Generator:
    yield {
        "valid_scope": "1",
        "invalid_scope": "0",
    }


class TestCacheFeeds:
    pass  # TODO: route not yet implemented

    # def test_cache_feeds_valid_data(self: "TestCacheFeeds", cach_feed_test_data: Dict[str, Any]) -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.post(f"/feeds/cacheFeeds/{cach_feed_test_data['valid_scope']}", headers=headers)
    #     assert response.status_code == 200
    #     assert response.json()["success"] is True

    # def test_cache_feeds_invalid_data(self: "TestCacheFeeds", cach_feed_test_data: Dict[str, Any]) -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.post(f"/feeds/cacheFeeds/{cach_feed_test_data['invalid_scope']}", headers=headers)
    #     assert response.status_code == 400

    # def test_cache_feeds_response_format(self: "TestCacheFeeds", cach_feed_test_data: Dict[str, Any]) -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.post(f"/feeds/cacheFeeds/{cach_feed_test_data['valid_scope']}", headers=headers)
    #     assert response.headers["Content-Type"] == "application/json"

    # def test_cache_feeds_authorization(self: "TestCacheFeeds", cach_feed_test_data: Dict[str, Any]) -> None:
    #     headers = {"authorization": ""}
    #     response = client.post(f"/feeds/cacheFeeds/{cach_feed_test_data['valid_scope']}", headers=headers)
    #     assert response.status_code == 401


class TestFetchFeeds:
    pass  # TODO: route not yet implemented

    # def test_fetch_from_feed_existing_id(self: "TestFetchFeeds", feed_test_ids: Dict[str, Any]) -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.get(f"/feeds/fetchFromFeed/{feed_test_ids['valid_feed_id']}", headers=headers)
    #     assert response.status_code == 200
    #     assert "result" in response.json()

    # def test_fetch_from_feed_invalid_id(self: "TestFetchFeeds", feed_test_ids: Dict[str, Any]) -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.get(f"/feeds/fetchFromFeed/{feed_test_ids['invalid_feed_id']}", headers=headers)
    #     assert response.status_code == 422

    # def test_fetch_from_feed_non_existing_id(self: "TestFetchFeeds", feed_test_ids: Dict[str, Any]) -> None:
    #     response = client.get(f"/feeds/fetchFromFeed/{feed_test_ids['non_existing_feed_id']}")
    #     assert response.status_code in (404, 405)

    # def test_fetch_from_feed_response_format(self: "TestFetchFeeds", feed_test_ids: Dict[str, Any]) -> None:
    #     response = client.get(f"/feeds/fetchFromFeed/{feed_test_ids['valid_feed_id']}")
    #     assert response.headers["Content-Type"] == "application/json"


class TestGetFeedByIdInfo:
    def test_get_existing_feed_details(self: "TestGetFeedByIdInfo", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        response = client.get(f"/feeds/{feed_id}")
        assert response.status_code == 200
        assert response.json()["feed"]["id"] == feed_id
        assert response.json()["feed"]["name"] == feed_data["name"]

    def test_get_invalid_feed_by_id(self: "TestGetFeedByIdInfo", feed_test_ids: Dict[str, Any]) -> None:
        response = client.get(f"/feeds/{feed_test_ids['invalid_feed_id']}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Feed not found."

    def test_get_non_existing_feed_details(self: "TestGetFeedByIdInfo", feed_test_ids: Dict[str, Any]) -> None:
        response = client.get(f"/feeds/{feed_test_ids['non_existing_feed_id']}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Feed not found."

    def test_get_feed_response_format(self: "TestGetFeedByIdInfo", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        response = client.get(f"/feeds/{feed_id}")
        assert response.headers["Content-Type"] == "application/json"
        data = response.json()
        assert "feed" in data
        assert data["feed"]["id"] == feed_id
        assert data["feed"]["name"] == feed_data["name"]


class TestUpdateFeed:
    def test_update_existing_feed(self: "TestUpdateFeed", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

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

    def test_update_non_existing_feed(
        self: "TestUpdateFeed", feed_test_ids: Dict[str, Any], feed_data: Dict[str, Any]
    ) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.put(f"/feeds/{feed_test_ids['non_existing_feed_id']}", json=feed_data, headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Feed not found."

    def test_update_feed_response_format(self: "TestUpdateFeed", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

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

    def test_update_feed_authorization(self: "TestUpdateFeed", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        headers = {"authorization": ""}
        response = client.put(f"/feeds/{feed_id}", json=feed_data, headers=headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"


class TestToggleFeed:
    def test_toggle_existing_feed(self: "TestToggleFeed", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

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

    def test_toggle_non_existing_feed(self: "TestToggleFeed", feed_test_ids: Dict[str, Any]) -> None:
        toggle_data = {"enable": True}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.patch(f"feeds/{feed_test_ids['non_existing_feed_id']}", json=toggle_data, headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Feed not found."

    def test_toggle_feed_response_format(self: "TestToggleFeed", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

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

    def test_toggle_feed_authorization(self: "TestToggleFeed", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        feed_id = response.json()["feed"]["id"]
        assert response.status_code == 201

        toggle_data = {"enable": True}
        headers = {"authorization": ""}
        response = client.patch(f"feeds/{feed_id}", json=toggle_data, headers=headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"


class TestFetschFromAllFeeds:
    pass  # TODO: route not yet implemented

    # def test_fetch_data_from_all_feeds(self: "TestFetschFromAllFeeds") -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.get("/feeds/fetchFromAllFeeds", headers=headers)
    #     assert response.status_code == 200
    #     response_data = response.json()
    #     assert "result" in response_data

    # def test_fetch_from_all_feeds_response_format(self: "TestFetschFromAllFeeds") -> None:
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.get("/feeds/fetchFromAllFeeds", headers=headers)
    #     assert response.headers["Content-Type"] == "application/json"
    #     assert "result" in response.json()


class TestGetAllFeeds:
    def test_get_all_feeds(self: "TestGetAllFeeds", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        assert response.status_code == 201

        response = client.get("/feeds")
        assert response.status_code == 200
        assert isinstance(response.json()["feeds"], list)

    def test_get_feeds_response_format(self: "TestGetAllFeeds", feed_data: Dict[str, Any]) -> None:
        db = get_db()

        sharing_group = SharingGroup(
            name="test_group", releasability="", organisation_uuid="", org_id=1, sync_user_id=1
        )
        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)
        feed_data["sharing_group_id"] = sharing_group.id

        tag = Tag(
            name="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            colour="#FFFFFF",
            exportable=False,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        feed_data["tag_id"] = tag.id

        event = Event(info="test")
        db.add(event)
        db.commit()
        db.refresh(event)
        feed_data["event_id"] = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)
        assert response.status_code == 201

        response = client.get("/feeds")
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
