import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff

@pytest.mark.asyncio
async def test_valid_search_attribute_data_site_admin(db: AsyncSession, auth_key, client) -> None:
    def preprocessor(modern, legacy):
        del modern["Event"]["Tag"]
        del modern["Event"]["Attribute"]["Tag"]

    path = "/events/restSearch"
    request_body = {"returnFormat": "json", "limit": 100, "distribution": 0}
    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}
