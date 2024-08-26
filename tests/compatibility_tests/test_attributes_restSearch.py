import httpx
import pytest
from deepdiff import DeepDiff
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession


def to_legacy_format(data):
    if isinstance(data, bool):
        return data
    elif isinstance(data, (int, float)):
        return str(data)
    elif isinstance(data, dict):
        return {key: to_legacy_format(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [to_legacy_format(x) for x in data]
    return data


def get_legacy_modern_diff(http_method, path, body, auth_key, client):
    clear_key, auth_key = auth_key
    headers = {"authorization": clear_key, "accept": "application/json"}

    print("-" * 50)
    print(f"Calling {path}")
    ic(body)

    call = getattr(client, http_method)
    response = call(path, json=body, headers=headers)
    response_json = response.json()
    response_json_in_legacy = to_legacy_format(response_json)

    call = getattr(httpx, http_method)
    legacy_response = call(f"http://misp-core{path}", json=body, headers=headers)
    ic(legacy_response)
    legacy_response_json = legacy_response.json()
    ic("Modern MISP Response")
    ic(response_json)
    ic("Legacy MISP Response")
    ic(legacy_response_json)

    diff = DeepDiff(response_json_in_legacy, legacy_response_json, verbose_level=2)
    ic(diff)

    # remove None values added in Modern MISP.
    # They shouldnt hurt and removing all None
    # overshoots, MISP is inconsistent when to include what.
    # Note: We don't want the opposite. If MISP includes None, Modern MISP should do this as well!
    diff["dictionary_item_removed"] = {k: v for k, v in diff["dictionary_item_removed"].items() if v is not None}
    if diff["dictionary_item_removed"] == {}:
        del diff["dictionary_item_removed"]

    return diff


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
