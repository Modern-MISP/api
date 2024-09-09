import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_attribute_describe_types(db: AsyncSession, auth_key, client) -> None:
    path = "/attributes/describeTypes"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}
