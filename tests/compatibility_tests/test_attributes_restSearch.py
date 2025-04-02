import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_valid_search_attribute_data(db: AsyncSession, attribute, auth_key, client) -> None:
    request_body = {"returnFormat": "json", "limit": 100, "value": attribute.value}
    path = "/attributes/restSearch"

    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_valid_search_multi_attribute_data(
    db: AsyncSession, attribute_multi, attribute_multi2, auth_key, client
) -> None:
    assert attribute_multi.value != attribute_multi2.value
    request_body = {"returnFormat": "json", "limit": 100, "value": attribute_multi.value1}
    path = "/attributes/restSearch"

    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_valid_search_tag_attribute_data(db: AsyncSession, attribute_with_normal_tag, auth_key, client) -> None:
    attribute, attribute_tag = attribute_with_normal_tag
    request_body = {"returnFormat": "json", "limit": 100, "value": attribute.value}
    path = "/attributes/restSearch"

    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_valid_search_local_tag_attribute_data(
    db: AsyncSession, attribute_with_local_tag, auth_key, client
) -> None:
    request_body = {"returnFormat": "json", "limit": 100, "value": attribute_with_local_tag.value}
    path = "/attributes/restSearch"

    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_valid_search_non_exportable_local_tag_attribute_data(
    db: AsyncSession, attribute_with_non_exportable_local_tag, auth_key, client
) -> None:
    request_body = {"returnFormat": "json", "limit": 100, "value": attribute_with_non_exportable_local_tag.value}
    path = "/attributes/restSearch"

    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_valid_search_galaxy_tag_attribute_data(
    db: AsyncSession, attribute_with_galaxy_cluster_one_tag, auth_key, client
) -> None:
    request_body = {"returnFormat": "json", "limit": 100, "value": attribute_with_galaxy_cluster_one_tag.value}
    path = "/attributes/restSearch"

    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_valid_search_attribute_data_site_admin(db: AsyncSession, auth_key, client) -> None:
    def preprocessor(modern, legacy):
        del modern["Event"]["Tag"]
        del modern["Event"]["Attribute"]["Tag"]

    path = "/events/restSearch"
    request_body = {"returnFormat": "json", "limit": 100, "distribution": 0}
    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}
