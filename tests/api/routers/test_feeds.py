from typing import Any, Dict, Generator

import pytest

from ...environment import client, environment
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
        generate_random_valid_feed_data().dict(),
        generate_random_valid_feed_data().dict(),
    ]
)
def feed_data(request: Any) -> Dict[str, Any]:
    return request.param


# --- Test cases ---


# Test add a feed
def test_add_feed(feed_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/feeds/", json=feed_data, headers=headers)

    assert response.status_code == 201


def test_feed_error_handling() -> None:
    invalid_data = {"name": "Test Feed"}
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/feeds/", json=invalid_data, headers=headers)
    assert response.status_code == 422


def test_feed_response_format(feed_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post("/feeds/", json=feed_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"


def test_add_feed_authorization(feed_data: Dict[str, Any]) -> None:
    headers = {"authorization": ""}
    response = client.post("/feeds/", json=feed_data, headers=headers)
    assert response.status_code == 401


# Test enable feed
@pytest.fixture(scope="module")
def feed_test_ids() -> Generator:
    yield {
        "valid_feed_id": "1",
        "non_existing_feed_id": "0",
        "invalid_feed_id": "invalid",
    }


def test_enable_feed(feed_test_ids: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"feeds/enable/{feed_test_ids['valid_feed_id']}", headers=headers)
    assert response.status_code == 200

    response = client.post(f"feeds/enable/{feed_test_ids['non_existing_feed_id']}", headers=headers)
    assert response.status_code == 404

    response = client.post(f"feeds/enable/{feed_test_ids['invalid_feed_id']}", headers=headers)
    assert response.status_code == 422


def test_feed_enable_response_format(feed_test_ids: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"feeds/enable/{feed_test_ids['valid_feed_id']}", headers=headers)
    assert response.headers["Content-Type"] == "application/json"


def test_enable_feed_authorization(feed_test_ids: Dict[str, Any]) -> None:
    headers = {"authorization": ""}
    response = client.post(f"feeds/enable/{feed_test_ids['valid_feed_id']}", headers=headers)
    assert response.status_code == 401


# Test disable feed
def test_feed_disable(feed_test_ids: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"feeds/disable/{feed_test_ids['valid_feed_id']}", headers=headers)
    assert response.status_code == 200

    response = client.post(f"feeds/disable/{feed_test_ids['non_existing_feed_id']}", headers=headers)
    assert response.status_code == 404

    response = client.post(f"feeds/disable/{feed_test_ids['invalid_feed_id']}", headers=headers)
    assert response.status_code == 422


def test_feed_disable_response_format(feed_test_ids: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"feeds/disable/{feed_test_ids['valid_feed_id']}", headers=headers)
    assert response.headers["Content-Type"] == "application/json"


def test_disable_feed_authorization(feed_test_ids: Dict[str, Any]) -> None:
    headers = {"authorization": ""}
    response = client.post(f"feeds/enable/{feed_test_ids['valid_feed_id']}", headers=headers)
    assert response.status_code == 401


@pytest.fixture(scope="module")
def cach_feed_test_data() -> Generator:
    yield {
        "valid_scope": "1",
        "invalid_scope": "0",
    }


# # Test cache Feed in a scope
# # TODO: route not yet implemented
# def test_cache_feeds_valid_data(cach_feed_test_data: Dict[str, Any]) -> None:
#     headers = {"authorization": environment.site_admin_user_token}
#     response = client.post(f"/feeds/cacheFeeds/{cach_feed_test_data['valid_scope']}", headers=headers)
#     assert response.status_code == 200
#     assert response.json()["success"] is True


# # TODO: route not yet implemented
# def test_cache_feeds_invalid_data(cach_feed_test_data: Dict[str, Any]) -> None:
#     headers = {"authorization": environment.site_admin_user_token}
#     response = client.post(f"/feeds/cacheFeeds/{cach_feed_test_data['invalid_scope']}", headers=headers)
#     assert response.status_code == 400


def test_cache_feeds_response_format(cach_feed_test_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.post(f"/feeds/cacheFeeds/{cach_feed_test_data['valid_scope']}", headers=headers)
    assert response.headers["Content-Type"] == "application/json"


def test_cache_feeds_authorization(cach_feed_test_data: Dict[str, Any]) -> None:
    headers = {"authorization": ""}
    response = client.post(f"/feeds/cacheFeeds/{cach_feed_test_data['valid_scope']}", headers=headers)
    assert response.status_code == 401


# # Test fetch from feed
# # TODO: route not yet implemented
# def test_fetch_from_feed_existing_id(feed_test_ids: Dict[str, Any]) -> None:
#     response = client.get(f"/feeds/fetchFromFeed/{feed_test_ids['valid_feed_id']}")
#     assert response.status_code == 200
#     assert "result" in response.json()

# # TODO: route not yet implemented
# def test_fetch_from_feed_invalid_id(feed_test_ids: Dict[str, Any]) -> None:
#     response = client.get(f"/feeds/fetchFromFeed/{feed_test_ids['invalid_feed_id']}")
#     assert response.status_code == 422


def test_fetch_from_feed_non_existing_id(feed_test_ids: Dict[str, Any]) -> None:
    response = client.get(f"/feeds/fetchFromFeed/{feed_test_ids['non_existing_feed_id']}")
    assert response.status_code in (404, 405)


def test_fetch_from_feed_response_format(feed_test_ids: Dict[str, Any]) -> None:
    response = client.get(f"/feeds/fetchFromFeed/{feed_test_ids['valid_feed_id']}")
    assert response.headers["Content-Type"] == "application/json"


# Test get feed by id
def test_get_existing_feed_details(feed_test_ids: Dict[str, Any]) -> None:
    response = client.get(f"/feeds/{feed_test_ids['valid_feed_id']}")
    assert response.status_code == 200
    assert response.json()["feed"][0]["id"] == feed_test_ids["valid_feed_id"]


def test_get_invalid_feed_by_id(feed_test_ids: Dict[str, Any]) -> None:
    response = client.get(f"/feeds/{feed_test_ids['invalid_feed_id']}")
    assert response.status_code == 404


def test_get_non_existing_feed_details(feed_test_ids: Dict[str, Any]) -> None:
    response = client.get(f"/feeds/{feed_test_ids['non_existing_feed_id']}")
    assert response.status_code == 404


def test_get_feed_response_format(feed_test_ids: Dict[str, Any]) -> None:
    response = client.get(f"/feeds/{feed_test_ids['valid_feed_id']}")
    assert response.headers["Content-Type"] == "application/json"
    data = response.json()
    assert "feed" in data
    assert isinstance(data["feed"], list)


# Test update feed
def test_update_existing_feed(feed_test_ids: Dict[str, Any], feed_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.put(f"/feeds/{feed_test_ids['valid_feed_id']}", json=feed_data, headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["feed"][0]["name"] == feed_data["name"]


def test_update_non_existing_feed(feed_test_ids: Dict[str, Any], feed_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.put(f"/feeds/{feed_test_ids['non_existing_feed_id']}", json=feed_data, headers=headers)
    assert response.status_code == 404


def test_update_feed_response_format(feed_test_ids: Dict[str, Any], feed_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}
    response = client.put(f"/feeds/{feed_test_ids['valid_feed_id']}", json=feed_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    assert "feed" in response.json()


def test_update_feed_authorization(feed_test_ids: Dict[str, Any], feed_data: Dict[str, Any]) -> None:
    headers = {"authorization": ""}
    response = client.put(f"/feeds/{feed_test_ids['valid_feed_id']}", json=feed_data, headers=headers)
    assert response.status_code == 401


# Test toggle feed
def test_toggle_existing_feed(feed_test_ids: Dict[str, Any]) -> None:
    toggle_data = {"enable": True}
    headers = {"authorization": environment.site_admin_user_token}
    response = client.patch(f"feeds/{feed_test_ids['valid_feed_id']}", json=toggle_data, headers=headers)
    assert response.status_code == 200


def test_toggle_non_existing_feed(feed_test_ids: Dict[str, Any]) -> None:
    toggle_data = {"enable": True}
    headers = {"authorization": environment.site_admin_user_token}
    response = client.patch(f"feeds/{feed_test_ids['non_existing_feed_id']}", json=toggle_data, headers=headers)
    assert response.status_code == 404


def test_toggle_feed_response_format(feed_test_ids: Dict[str, Any]) -> None:
    toggle_data = {"enable": True}
    headers = {"authorization": environment.site_admin_user_token}
    response = client.patch(f"feeds/{feed_test_ids['valid_feed_id']}", json=toggle_data, headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    data = response.json()
    assert "name" in data
    assert "message" in data
    assert "url" in data


def test_toggle_feed_scenarios(feed_data: Dict[str, Any]) -> None:
    headers = {"authorization": environment.site_admin_user_token}

    response = client.post("/feeds/", json=feed_data, headers=headers)
    response_json = response.json()
    feed_id = response_json["feed"][0]["id"]

    # Activate the feed
    response = client.patch(f"/feeds/{feed_id}", json={"enable": 1}, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Feed enabled successfully"

    # Check whether the feed is already activated
    response = client.patch(f"/feeds/{feed_id}", json={"enable": 1}, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Feed already enabled"

    # Deactivate the feed
    response = client.patch(f"/feeds/{feed_id}", json={"enable": 0}, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Feed disabled successfully"

    # Check whether the feed is already deactivated
    response = client.patch(f"/feeds/{feed_id}", json={"enable": 0}, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Feed already disabled"


def test_toggle_feed_authorization(feed_test_ids: Dict[str, Any]) -> None:
    toggle_data = {"enable": True}
    headers = {"authorization": ""}
    response = client.patch(f"feeds/{feed_test_ids['valid_feed_id']}", json=toggle_data, headers=headers)
    assert response.status_code == 401


# # Test fetsch from all feeds
# # TODO: route not yet implemented
# def test_fetch_data_from_all_feeds() -> None:
#     response = client.get("/feeds/fetchFromAllFeeds")
#     assert response.status_code == 200
#     response_data = response.json()
#     assert "result" in response_data


# # TODO: route not yet implemented
# def test_fetch_from_all_feeds_response_format() -> None:
#     response = client.get("/feeds/fetchFromAllFeeds")
#     assert response.headers["Content-Type"] == "application/json"
#     assert "result" in response.json()


# Test get all feeds
def test_get_all_feeds() -> None:
    response = client.get("/feeds/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    print(response.json())


def test_get_feeds_response_format() -> None:
    response = client.get("/feeds/")
    assert response.headers["Content-Type"] == "application/json"
    response_data = response.json()

    assert isinstance(response_data, list)

    # Test all required fields
    for feed_wrapper in response_data:
        assert "feed" in feed_wrapper
        for feed in feed_wrapper["feed"]:
            assert "id" in feed
            assert "name" in feed
            assert "provider" in feed
            assert "url" in feed
