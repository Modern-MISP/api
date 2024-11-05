import random
from typing import Any, Dict

import pytest
import pytest_asyncio
from sqlalchemy.orm import Session

from mmisp.db.models.tag import Tag
from mmisp.tests.generators.model_generators.organisation_generator import generate_organisation
from tests.api.helpers.tags_helper import (
    generate_invalid_tag_data,
    generate_valid_required_tag_data,
    generate_valid_tag_data,
    get_invalid_tags,
    get_non_existing_tags,
    random_string_with_punctuation,
    remove_tags,
)


@pytest.fixture(
    params=[
        generate_valid_tag_data,
        generate_valid_required_tag_data,
    ]
)
def tag_data(request: Any, organisation, site_admin_user) -> Dict[str, Any]:
    return request.param(organisation, site_admin_user).dict()


@pytest_asyncio.fixture
async def add_tags(db, site_admin_user):
    tags = []
    orgs = []

    async def create_tags(amount=5):
        for _ in range(amount):
            org = generate_organisation()
            db.add(org)
            await db.commit()
            orgs.append(org)
            new_tag = Tag(**generate_valid_tag_data(org, site_admin_user).dict())
            tags.append(new_tag)
            db.add(new_tag)
            await db.commit()
        return [x.id for x in tags]

    yield create_tags

    for x in tags:
        await db.delete(x)
    for x in orgs:
        await db.delete(x)
    await db.commit()


@pytest.fixture(
    params=[
        generate_invalid_tag_data(),
        generate_invalid_tag_data(),
    ]
)
def invalid_tag_data(request: Any) -> Dict[str, Any]:
    return request.param


@pytest.mark.asyncio
async def test_add_tag(db, tag_data: Dict[str, Any], site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags", json=tag_data, headers=headers)
    assert response.status_code == 201

    await remove_tags(db, [response.json()["Tag"]["id"]])


@pytest.mark.asyncio
async def test_add_tag_deprecated(db, tag_data: Dict[str, Any], site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags/add", json=tag_data, headers=headers)
    assert response.status_code == 201

    await remove_tags(db, [response.json()["Tag"]["id"]])


@pytest.mark.asyncio
async def test_add_tag_with_existing_name(db: Session, add_tags, site_admin_user_token, client) -> None:
    tag_id = await add_tags(1)
    tag_data = generate_valid_required_tag_data()
    tag_data.name = (await db.get(Tag, tag_id[0])).name
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags", json=tag_data.dict(), headers=headers)
    assert response.status_code == 403

    await remove_tags(db, tag_id)


@pytest.mark.asyncio
async def test_add_tag_with_existing_name_deprecated(db: Session, add_tags, site_admin_user_token, client) -> None:
    tag_id = await add_tags(1)
    tag_data = generate_valid_required_tag_data()
    tag_data.name = (await db.get(Tag, tag_id[0])).name
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags/add", json=tag_data.dict(), headers=headers)
    assert response.status_code == 403

    await remove_tags(db, tag_id)


@pytest.mark.asyncio
async def test_add_tag_with_invalid_colour(site_admin_user_token, client) -> None:
    tag_data = generate_valid_required_tag_data()
    tag_data.colour = "#12345,"
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags", json=tag_data.dict(), headers=headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_add_tag_invalid_data(invalid_tag_data: Any, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags", json=invalid_tag_data, headers=headers)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "field required" or "none is not an allowed value"


@pytest.mark.asyncio
async def test_add_tag_response_format(db, tag_data: Dict[str, Any], site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags", json=tag_data, headers=headers)

    json = response.json()
    assert json["Tag"]["name"] == tag_data["name"]
    assert json["Tag"]["colour"] == tag_data["colour"]
    assert json["Tag"]["exportable"] == tag_data["exportable"]

    await remove_tags(db, [response.json()["Tag"]["id"]])


@pytest.mark.asyncio
async def test_add_tag_response_format_deprecated(db, tag_data: Dict[str, Any], site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags/add", json=tag_data, headers=headers)

    json = response.json()
    assert json["Tag"]["name"] == tag_data["name"]
    assert json["Tag"]["colour"] == tag_data["colour"]
    assert json["Tag"]["exportable"] == tag_data["exportable"]

    await remove_tags(db, [response.json()["Tag"]["id"]])


@pytest.mark.asyncio
async def test_view_tag(db, add_tags, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    tags = await add_tags(5)
    non_existing_tags = await get_non_existing_tags(db)
    invalid_tags = get_invalid_tags()

    for tag in tags:
        response = client.get(f"/tags/{tag}", headers=headers)
        assert response.status_code == 200

    for non_existing_tag in non_existing_tags:
        response = client.get(f"/tags/{non_existing_tag}", headers=headers)
        assert response.status_code == 404

    for invalid_tag in invalid_tags:
        response = client.get(f"/tags/{invalid_tag}", headers=headers)
        assert response.status_code == 422

    await remove_tags(db, tags)


@pytest.mark.asyncio
async def test_view_tag_deprecated(db, add_tags, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    tags = await add_tags()
    non_existing_tags = await get_non_existing_tags(db)
    invalid_tags = get_invalid_tags()

    for tag in tags:
        response = client.get(f"/tags/view/{tag}", headers=headers)
        assert response.status_code == 200

    for non_existing_tag in non_existing_tags:
        response = client.get(f"/tags/view/{non_existing_tag}", headers=headers)
        assert response.status_code == 404

    for invalid_tag in invalid_tags:
        response = client.get(f"/tags/view/{invalid_tag}", headers=headers)
        assert response.status_code == 422

    await remove_tags(db, tags)


@pytest.mark.asyncio
async def test_view_tag_response_format(db, site_admin_user_token, add_tags, client) -> None:
    headers = {"authorization": site_admin_user_token}

    tag = await add_tags(1)

    response = client.get(f"tags/{tag[0]}", headers=headers)
    assert response.status_code == 200
    json = response.json()
    assert json["id"] == tag[0]

    await remove_tags(db, tag)


@pytest.mark.asyncio
async def test_view_tag_response_format_deprecated(db, site_admin_user_token, add_tags, client) -> None:
    headers = {"authorization": site_admin_user_token}

    tag = await add_tags(1)

    response = client.get(f"tags/view/{tag[0]}", headers=headers)
    assert response.status_code == 200
    json = response.json()
    assert json["id"] == tag[0]

    await remove_tags(db, tag)


@pytest.mark.asyncio
async def test_search_tag(db: Session, site_admin_user_token, add_tags, client) -> None:
    headers = {"authorization": site_admin_user_token}

    tags = await add_tags()

    for tag in tags:
        tag_name = (await db.get(Tag, tag)).name
        substring_start = random.randint(0, len(tag_name) - 1)
        substring_end = random.randint(substring_start + 1, len(tag_name))
        substring = tag_name[substring_start:substring_end]
        response = client.get(f"/tags/search/{substring}", headers=headers)
        assert response.status_code == 200

    name = random_string_with_punctuation(4)
    response = client.get(f"/tags/search/{name}", headers=headers)
    assert response.status_code == 200
    json = response.json()
    assert isinstance(json["response"], list)
    assert len(json["response"]) == 0

    await remove_tags(db, tags)


@pytest.mark.asyncio
async def test_search_tag_response_format(db: Session, site_admin_user_token, add_tags, client) -> None:
    headers = {"authorization": site_admin_user_token}
    tag = await add_tags(1)
    tag_name = (await db.get(Tag, tag[0])).name
    substring_start = random.randint(0, len(tag_name) - 1)
    substring_end = random.randint(substring_start + 1, len(tag_name))
    substring = tag_name[substring_start:substring_end]

    response = client.get(f"tags/search/{substring}", headers=headers)
    assert response.status_code == 200
    json = response.json()
    assert isinstance(json["response"], list)

    await remove_tags(db, tag)


@pytest.mark.asyncio
async def test_edit_tag(db, tag_data: Dict[str, Any], site_admin_user_token, add_tags, client) -> None:
    headers = {"authorization": site_admin_user_token}

    tags = await add_tags()
    tag_data.pop("name")
    for tag in tags:
        response = client.put(f"/tags/{tag}", json=tag_data, headers=headers)
        assert response.status_code == 200

    non_existing_tags = await get_non_existing_tags(db)
    for non_existing_tag in non_existing_tags:
        response = client.put(f"/tags/{non_existing_tag}", json=tag_data, headers=headers)
        assert response.status_code == 404

    invalid_tags = get_invalid_tags()
    for invalid_tag in invalid_tags:
        response = client.put(f"/tags/{invalid_tag}", json=tag_data, headers=headers)
        assert response.status_code == 422

    await remove_tags(db, tags)


@pytest.mark.asyncio
async def test_edit_tag_deprecated(db, tag_data: Dict[str, Any], site_admin_user_token, add_tags, client) -> None:
    headers = {"authorization": site_admin_user_token}

    tags = await add_tags(1)
    for tag in tags:
        response = client.post(f"/tags/edit/{tag}", json=tag_data, headers=headers)
        assert response.status_code == 200

    non_existing_tags = await get_non_existing_tags(db)
    for non_existing_tag in non_existing_tags:
        response = client.post(f"/tags/edit/{non_existing_tag}", json=tag_data, headers=headers)
        assert response.status_code == 404

    invalid_tags = get_invalid_tags()
    for invalid_tag in invalid_tags:
        response = client.post(f"/tags/edit/{invalid_tag}", json=tag_data, headers=headers)
        assert response.status_code == 422

    await remove_tags(db, tags)


@pytest.mark.asyncio
async def test_edit_tag_same_name(db: Session, site_admin_user_token, add_tags, client) -> None:
    headers = {"authorization": site_admin_user_token}

    tags = await add_tags(2)
    name = (await db.get(Tag, tags[0])).name

    response = client.put(f"/tags/{tags[1]}", json={"name": name}, headers=headers)
    assert response.status_code == 403

    await remove_tags(db, tags)


@pytest.mark.asyncio
async def test_edit_tag_same_name_deprecated(db: Session, site_admin_user_token, add_tags, client) -> None:
    headers = {"authorization": site_admin_user_token}

    tags = await add_tags(2)
    name = (await db.get(Tag, tags[0])).name

    response = client.post(f"/tags/edit/{tags[1]}", json={"name": name}, headers=headers)
    assert response.status_code == 403

    await remove_tags(db, tags)


@pytest.mark.asyncio
async def test_edit_tag_response_format(db, tag_data: Dict[str, Any], site_admin_user_token, add_tags, client) -> None:
    tag = await add_tags(1)

    headers = {"authorization": site_admin_user_token}
    response = client.put(f"tags/{tag[0]}", json=tag_data, headers=headers)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    json = response.json()
    print(json)
    assert json["Tag"]["id"] == tag[0]

    await remove_tags(db, tag)


@pytest.mark.asyncio
async def test_delete_tag(db, site_admin_user_token, add_tags, client) -> None:
    headers = {"authorization": site_admin_user_token}

    tags = await add_tags()

    for tag in tags:
        response = client.delete(f"/tags/{tag}", headers=headers)
        assert response.status_code == 200

    non_existing_tags = await get_non_existing_tags(db)
    for non_existing_tag in non_existing_tags:
        response = client.delete(f"/tags/{non_existing_tag}", headers=headers)
        assert response.status_code == 404

    invalid_tags = get_invalid_tags()
    for invalid_tag in invalid_tags:
        response = client.delete(f"/tags/{invalid_tag}", headers=headers)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_tag_deprecated(site_admin_user_token, add_tags, client) -> None:
    headers = {"authorization": site_admin_user_token}

    tags = await add_tags()

    for tag in tags:
        response = client.post(f"/tags/delete/{tag}", headers=headers)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_edit_delete_response_format(site_admin_user_token, add_tags, client) -> None:
    headers = {"authorization": site_admin_user_token}
    tag = await add_tags(1)
    response = client.delete(f"tags/{tag[0]}", headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    json = response.json()
    assert json["name"] == "Tag deleted."


@pytest.mark.asyncio
async def test_edit_delete_response_format_deprecated(site_admin_user_token, add_tags, client) -> None:
    headers = {"authorization": site_admin_user_token}
    tag = await add_tags(1)
    response = client.post(f"tags/delete/{tag[0]}", headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    json = response.json()
    assert json["name"] == "Tag deleted."


@pytest.mark.asyncio
async def test_get_all_tags(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/tags", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_all_tags_response_format(db, site_admin_user_token, add_tags, client) -> None:
    tags = await add_tags(1)

    headers = {"authorization": site_admin_user_token}
    response = client.get("/tags", headers=headers)
    assert response.headers["Content-Type"] == "application/json"

    json = response.json()

    assert isinstance(json["Tag"], list)

    assert "Tag" in json
    for tag_wrapper in json["Tag"]:
        assert "id" in tag_wrapper
        assert "name" in tag_wrapper
        assert "colour" in tag_wrapper
        assert "exportable" in tag_wrapper

    await remove_tags(db, tags)
