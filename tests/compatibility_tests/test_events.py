import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


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
    path = "/events"

    request_body = {"info": "test ents from lotr", "distribution": 0}

    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_add_event_data_empty_string(db, auth_key, client) -> None:
    path = "/events"

    request_body = {"info": "test ents", "date": "", "distribution": 0}

    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}
