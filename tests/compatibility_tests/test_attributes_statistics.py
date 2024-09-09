import asyncio

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.db.models.attribute import Attribute
from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest_asyncio.fixture
async def attribute_for_statistics(db, event):
    """
    Add 12 attributes
        1 -> 8.33%
        2 -> 16.66%
        3 -> 25%
        4 -> 33.33%
        5 -> 41.66%
        6 -> 50%
        7 -> 58.33%
        8 -> 66.66%
        9 -> 75%
        10 -> 83.33%
        11 -> 91.66%
        12 -> 100%

    """
    event_id = event.id
    a = [
        Attribute(value="1.2.3.5", type="ip-src", category="Network activity", event_id=event_id),
        Attribute(value="1.2.3.6", type="ip-src", category="Network activity", event_id=event_id),
        Attribute(value="1.2.3.7", type="ip-src", category="Network activity", event_id=event_id),
        Attribute(value="1.2.3.8", type="ip-dst", category="Payload delivery", event_id=event_id),
        Attribute(value="1", type="integer", category="Other", event_id=event_id),
        Attribute(value="2", type="integer", category="Other", event_id=event_id),
        Attribute(value="3", type="integer", category="Other", event_id=event_id),
        Attribute(value="4", type="integer", category="Other", event_id=event_id),
        Attribute(value="5", type="integer", category="Other", event_id=event_id),
        Attribute(value="6", type="integer", category="Other", event_id=event_id),
        Attribute(value="7", type="integer", category="Other", event_id=event_id),
        Attribute(value="8", type="integer", category="Other", event_id=event_id),
    ]
    db.add_all(a)
    event.attribute_count += len(a)
    await db.commit()
    yield a

    await asyncio.gather(*[db.delete(elem) for elem in a])

    event.attribute_count -= len(a)
    await db.commit()


@pytest.mark.asyncio
async def test_attribute_statistics_category_absolute(
    db: AsyncSession, attribute_for_statistics, auth_key, client
) -> None:
    path = "/attributes/attributeStatistics/category/0"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_attribute_statistics_category_relative(
    db: AsyncSession, attribute_for_statistics, auth_key, client
) -> None:
    path = "/attributes/attributeStatistics/category/1"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_attribute_statistics_type_absolute(db: AsyncSession, attribute_for_statistics, auth_key, client) -> None:
    path = "/attributes/attributeStatistics/type/0"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_attribute_statistics_type_relative(db: AsyncSession, attribute_for_statistics, auth_key, client) -> None:
    path = "/attributes/attributeStatistics/type/1"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}
