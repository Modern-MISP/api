import pytest
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_restsearch_no_return_format(db: AsyncSession, event, site_admin_user_token, client) -> None:
    request_body = {"page": 1, "limit": 100}

    headers = {"authorization": site_admin_user_token}
    response = client.post("/attributes/restSearch", json=request_body, headers=headers)
    if response.status_code > 300:
        print(response.json())
    assert response.status_code == 200
    response_json = response.json()
    assert "response" in response_json
    assert isinstance(response_json["response"]["Attribute"], list)


@pytest.mark.asyncio
async def test_valid_search_attribute_data(
    db: AsyncSession, event, site_admin_user_token, sharing_group, client
) -> None:
    request_body = {"returnFormat": "json", "limit": 100}

    event.sharing_group_id = sharing_group.id
    await db.commit()

    headers = {"authorization": site_admin_user_token}
    response = client.post("/attributes/restSearch", json=request_body, headers=headers)
    if response.status_code > 300:
        print(response.json())
    assert response.status_code == 200
    response_json = response.json()
    assert "response" in response_json
    assert isinstance(response_json["response"]["Attribute"], list)


@pytest.mark.asyncio
async def test_not_implemented_restsearch(
    db: AsyncSession, event, site_admin_user_token, sharing_group, client
) -> None:
    request_body = {"limit": 100, "to": 1234567}

    event.sharing_group_id = sharing_group.id
    await db.commit()

    headers = {"authorization": site_admin_user_token}
    response = client.post("/attributes/restSearch", json=request_body, headers=headers)
    response_json = response.json()
    ic(response_json)
    assert response.status_code == 501


@pytest.mark.asyncio
async def test_invalid_search_attribute_data(site_admin_user_token, client) -> None:
    request_body = {"returnFormat": "invalid format"}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/attributes/restSearch", json=request_body, headers=headers)
    assert response.status_code == 404
