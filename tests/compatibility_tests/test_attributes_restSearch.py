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


@pytest.mark.asyncio
async def test_valid_search_attribute_data(db: AsyncSession, attribute, auth_key, client) -> None:
    clear_key, auth_key = auth_key
    ic(clear_key)
    request_body = {"returnFormat": "json", "limit": 100, "value": attribute.value}

    headers = {"authorization": clear_key, "accept": "application/json"}
    response = client.post("/attributes/restSearch", json=request_body, headers=headers)
    response_json = response.json()
    response_json_in_legacy = to_legacy_format(response_json)

    legacy_response = httpx.post("http://misp-core/attributes/restSearch", headers=headers, json=request_body)
    ic(legacy_response)
    legacy_response_json = legacy_response.json()
    ic(response_json)
    ic(legacy_response_json)
    assert DeepDiff(response_json_in_legacy, legacy_response_json) == {}
