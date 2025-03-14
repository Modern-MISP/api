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


@pytest.mark.asyncio
async def test_valid_search_attribute_data_read_only_user(
        db: AsyncSession, access_test_objects, client) -> None:
    def preprocess(modern, legacy):
        del modern["response"][0]["Event"]["Tag"]
        del modern["response"][0]["Event"]["Attribute"][0]["Tag"]
        del modern["response"][0]["Event"]["event_creator_email"]

    path = "/events/restSearch"
    request_body = {"returnFormat": "json", "limit": 100, "distribution": 0}
    clear_key = access_test_objects["default_read_only_user_clear_key"]
    auth_key = access_test_objects["default_read_only_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client, preprocess) == {}


@pytest.mark.asyncio
async def test_valid_search_attribute_data(db: AsyncSession, access_test_objects, client) -> None:
    def preprocessor(modern, legacy):
        del modern["response"][0]["Event"]["Tag"]
        del modern["response"][0]["Event"]["Attribute"][0]["Tag"]

    path = "/events/restSearch"
    request_body = {"returnFormat": "json", "limit": 100, "distribution": 0}
    clear_key = access_test_objects["default_user_clear_key"]
    auth_key = access_test_objects["default_user_auth_key"]
    assert get_legacy_modern_diff("post", path, request_body, (clear_key, auth_key), client, preprocessor) == {}
