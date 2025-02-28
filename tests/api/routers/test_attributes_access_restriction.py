import pytest
import pytest_asyncio
import sqlalchemy as sa
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.db.models.attribute import AttributeTag
from mmisp.tests.generators.model_generators.tag_generator import generate_tag


@pytest.mark.asyncio
async def test_get_existing_attribute_read_only_user(
    db: AsyncSession,
    attribute_read_only_1,
    read_only_user_token,
    client,
) -> None:
    attribute, at = attribute_read_only_1
    attribute_id = attribute.id
    ic(attribute.asdict())
    headers = {"authorization": read_only_user_token}
    response = client.get(f"/attributes/{attribute_id}", headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_existing_attribute_fail_read_only_user(
    db: AsyncSession,
    attribute_with_normal_tag,
    read_only_user_token,
    client,
) -> None:
    attribute, at = attribute_with_normal_tag
    attribute_id = attribute.id
    ic(attribute.asdict())
    headers = {"authorization": read_only_user_token}
    response = client.get(f"/attributes/{attribute_id}", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_all_attributes_read_only_user(
    db: AsyncSession,
    event_read_only_1,
    read_only_user_token,
    sharing_group,
    organisation,
    attribute_read_only_1,
    client,
) -> None:
    event_read_only_1.sharing_group_id = sharing_group.id
    await db.commit()

    headers = {"authorization": read_only_user_token}
    response = client.get("/attributes", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 1
    for attribute in response_json:
        assert isinstance(response_json, list)
        assert "id" in attribute
        assert "event_id" in attribute
        assert "object_id" in attribute
        assert "object_relation" in attribute
        assert "category" in attribute
        assert "type" in attribute
        assert "value" in attribute
        assert "value1" in attribute
        assert "value2" in attribute
        assert "to_ids" in attribute
        assert "uuid" in attribute
        assert "timestamp" in attribute
        assert "distribution" in attribute
        assert "sharing_group_id" in attribute
        assert "comment" in attribute
        assert "deleted" in attribute
        assert "disable_correlation" in attribute
        assert "first_seen" in attribute
        assert "last_seen" in attribute

@pytest.mark.asyncio
async def test_delete_existing_attribute_read_only_user(read_only_user_token, attribute, client) -> None:
    attribute_id = attribute.id

    headers = {"authorization": read_only_user_token}
    response = client.delete(f"/attributes/{attribute_id}", headers=headers)

    assert response.status_code == 403





@pytest.mark.asyncio
async def test_add_attribute_valid_data_read_only_user(read_only_user_token, event, db, client) -> None:
    request_body = {
        "value": "1.2.3.4",
        "type": "ip-src",
        "category": "Network activity",
        "to_ids": True,
        "distribution": "1",
        "comment": "test comment",
        "disable_correlation": False,
    }
    event_id = event.id
    assert event.id is not None

    headers = {"authorization": read_only_user_token}
    response = client.post(f"/attributes/{event_id}", json=request_body, headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_existing_tag_to_attribute_read_only(
    db: AsyncSession, read_only_user_token, attribute, client
) -> None:
    attribute_id = attribute.id

    tag = generate_tag()
    setattr(tag, "user_id", 1)
    setattr(tag, "org_id", 1)

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    tag_id = tag.id

    headers = {"authorization": read_only_user_token}
    response = client.post(
        f"/attributes/addTag/{attribute_id}/{tag_id}/local:1",
        headers=headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_remove_existing_tag_from_attribute_read_only_user(read_only_user_token, attributetag, client) -> None:
    attribute_id = attributetag.attribute_id
    tag_id = attributetag.tag_id
    headers = {"authorization": read_only_user_token}
    response = client.post(f"/attributes/removeTag/{attribute_id}/{tag_id}", headers=headers)

    assert response.status_code == 403
