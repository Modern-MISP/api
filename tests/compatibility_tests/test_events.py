import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff
from api.tests.api.routers import delete_event

@pytest.mark.asyncio
async def test_view_event_normal_attribute_tag(db, event, attribute_with_normal_tag, auth_key, client) -> None:
    assert get_legacy_modern_diff("get", f"/events/view/{event.id}?extended=true", {}, auth_key, client) == {}


@pytest.mark.asyncio
async def test_view_event_galaxy_cluster_tag(
    db: AsyncSession, event, attribute_with_galaxy_cluster_one_tag, auth_key, client
) -> None:
    assert get_legacy_modern_diff("get", f"/events/view/{event.id}", {}, auth_key, client) == {}


@pytest.mark.asyncio
async def test_add_event_valid_data(
    db,
    auth_key,
    client,
) -> None:
    def preprocessor(modern, legacy):
        del modern["Event"]["timestamp"]
        del legacy["Event"]["timestamp"]
        del modern["Event"]["uuid"]
        del legacy["Event"]["uuid"]
        del modern["Event"]["id"]
        del legacy["Event"]["id"]

    path = "/events"
    request_body = {"info": "test events", "distribution": 0, "sharing_group_id": 0}

    assert get_legacy_modern_diff("post", path, request_body, auth_key, client, preprocessor) == {}

    await delete_event(db, 6)


@pytest.mark.asyncio
async def test_add_event_data_empty_string(db, auth_key, client) -> None:
    def preprocessor(modern, legacy):
        del modern["Event"]["timestamp"]
        del legacy["Event"]["timestamp"]
        del modern["Event"]["uuid"]
        del legacy["Event"]["uuid"]
        del modern["Event"]["id"]
        del legacy["Event"]["id"]

    path = "/events"
    request_body = {"info": "test events", "date": "", "distribution": 0, "sharing_group_id":0}

    assert get_legacy_modern_diff("post", path, request_body, auth_key, client, preprocessor) == {}


@pytest.mark.asyncio
async def test_get_existing_event(db, auth_key, client, event) -> None:
    path = f"/events/{event.id}"

    request_body = {}

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_get_non_existing_event(db, auth_key, client) -> None:
    path = f"/events/{9999}"

    request_body = {}

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_update_existing_event(db, auth_key, client, event) -> None:
    def preprocessor(modern, legacy):
        del modern["Event"]["timestamp"]
        del legacy["Event"]["timestamp"]

    path = f"/events/{event.id}"

    request_body = {"info": "updated info"}

    assert get_legacy_modern_diff("put", path, request_body, auth_key, client, preprocessor) == {}


@pytest.mark.asyncio
async def test_update_non_existing_event(db, auth_key, client) -> None:
    path = f"/events/{9999}"

    request_body = {"info": "updated info"}

    assert get_legacy_modern_diff("put", path, request_body, auth_key, client) == {}


# @pytest.mark.asyncio
# async def test_delete_existing_event(db, auth_key, client, event) -> None:
#
#    path = f"/events/{event.id}"
#
#    request_body = None
#
#    assert get_legacy_modern_diff("delete", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_delete_non_existing_event(db, auth_key, client) -> None:
    path = f"/events/{9999}"

    request_body = None

    assert get_legacy_modern_diff("delete", path, request_body, auth_key, client) == {}
