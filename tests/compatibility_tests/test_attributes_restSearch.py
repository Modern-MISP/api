import httpx
import pytest
import pytest_asyncio
from deepdiff import DeepDiff
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mmisp.db.models.attribute import Attribute
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement
from mmisp.db.models.tag import Tag


@pytest_asyncio.fixture
async def galaxy(db):
    galaxy = Galaxy(
        name="test galaxy",
        type="test galaxy type",
        description="test",
        version="1",
        kill_chain_order=None,
    )

    db.add(galaxy)
    await db.commit()
    await db.refresh(galaxy)

    yield galaxy

    await db.delete(galaxy)
    await db.commit()


@pytest_asyncio.fixture
async def galaxy_cluster_one(db, galaxy_cluster_one_tag, galaxy):
    galaxy_cluster = GalaxyCluster(
        collection_uuid="uuid",
        type="test type",
        value="test",
        tag_name=galaxy_cluster_one_tag.name,
        description="test",
        galaxy_id=galaxy.id,
        authors='["Konstantin Zangerle", "Test Writer"]',
    )

    db.add(galaxy_cluster)
    await db.commit()
    await db.refresh(galaxy_cluster)
    galaxy_element = GalaxyElement(galaxy_cluster_id=galaxy_cluster.id, key="refs", value="http://test-one.example.com")
    db.add(galaxy_element)
    await db.commit()

    yield galaxy_cluster

    await db.delete(galaxy_element)
    await db.delete(galaxy_cluster)
    await db.commit()


@pytest_asyncio.fixture
async def galaxy_cluster_two(db, galaxy_cluster_two_tag, galaxy):
    galaxy_cluster = GalaxyCluster(
        collection_uuid="uuid",
        type="test type",
        value="test",
        tag_name=galaxy_cluster_two_tag.name,
        description="test",
        galaxy_id=galaxy.id,
        authors="admin",
    )

    db.add(galaxy_cluster)
    await db.commit()
    await db.refresh(galaxy_cluster)
    galaxy_element = GalaxyElement(galaxy_cluster_id=galaxy_cluster.id, key="refs", value="http://test-two.example.com")
    db.add(galaxy_element)
    await db.commit()

    yield galaxy_cluster

    await db.delete(galaxy_element)
    await db.delete(galaxy_cluster)
    await db.commit()


@pytest_asyncio.fixture()
async def galaxy_cluster_one_tag(db, instance_owner_org):
    tag = Tag(
        name="test galaxy cluster one tag",
        colour="#123456",
        exportable=True,
        hide_tag=False,
        numerical_value=1,
        local_only=False,
        user_id=1,
        org_id=instance_owner_org.id,
        is_galaxy=True,
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    yield tag

    await db.delete(tag)
    await db.commit()


@pytest_asyncio.fixture()
async def galaxy_cluster_two_tag(db, instance_owner_org):
    tag = Tag(
        name="test galaxy cluster two tag",
        colour="#123456",
        exportable=True,
        hide_tag=False,
        numerical_value=2,
        local_only=False,
        user_id=1,
        org_id=instance_owner_org.id,
        is_galaxy=True,
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    yield tag

    await db.delete(tag)
    await db.commit()


@pytest_asyncio.fixture()
async def normal_tag(db, instance_owner_org):
    tag = Tag(
        name="test normal tag",
        colour="#123456",
        exportable=True,
        hide_tag=False,
        numerical_value=1,
        local_only=False,
        user_id=1,
        org_id=instance_owner_org.id,
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    yield tag

    await db.delete(tag)
    await db.commit()


@pytest_asyncio.fixture()
async def local_only_tag(db, instance_owner_org):
    tag = Tag(
        name="test local only tag",
        colour="#123456",
        exportable=True,
        hide_tag=False,
        numerical_value=1,
        local_only=True,
        user_id=1,
        org_id=instance_owner_org.id,
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    yield tag

    await db.delete(tag)
    await db.commit()


@pytest_asyncio.fixture()
async def non_exportable_local_only_tag(db, instance_owner_org):
    tag = Tag(
        name="test non exportable local only tag",
        colour="#123456",
        exportable=False,
        hide_tag=False,
        numerical_value=1,
        local_only=True,
        user_id=1,
        org_id=instance_owner_org.id,
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    yield tag

    await db.delete(tag)
    await db.commit()


@pytest_asyncio.fixture()
async def attribute_with_normal_tag(db, attribute, normal_tag):
    assert not normal_tag.local_only
    qry = (
        select(Attribute)
        .filter(Attribute.id == attribute.id)
        .options(selectinload(Attribute.attributetags))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)
    at = await attribute.add_tag(db, normal_tag)
    assert not at.local

    await db.commit()
    yield attribute

    await db.delete(at)
    await db.commit()


@pytest_asyncio.fixture()
async def attribute_with_local_tag(db, attribute, local_only_tag):
    qry = (
        select(Attribute)
        .filter(Attribute.id == attribute.id)
        .options(selectinload(Attribute.attributetags))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)
    at = await attribute.add_tag(db, local_only_tag)
    assert at.local

    await db.commit()
    yield attribute

    await db.delete(at)
    await db.commit()


@pytest_asyncio.fixture()
async def attribute_with_non_exportable_local_tag(db, attribute, non_exportable_local_only_tag):
    assert non_exportable_local_only_tag.local_only
    qry = (
        select(Attribute)
        .filter(Attribute.id == attribute.id)
        .options(selectinload(Attribute.attributetags))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)
    at = await attribute.add_tag(db, non_exportable_local_only_tag)

    await db.commit()
    yield attribute

    await db.delete(at)
    await db.commit()


@pytest_asyncio.fixture()
async def attribute_with_galaxy_cluster_one_tag(db, attribute, galaxy_cluster_one_tag):
    assert not galaxy_cluster_one_tag.local_only
    qry = (
        select(Attribute)
        .filter(Attribute.id == attribute.id)
        .options(selectinload(Attribute.attributetags))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)
    at = await attribute.add_tag(db, galaxy_cluster_one_tag)
    assert not at.local

    await db.commit()
    yield attribute

    await db.delete(at)
    await db.commit()


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

    ic("-" * 50)
    ic(f"Calling {path}")
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
    diff["dictionary_item_removed"] = {
        k: v for k, v in diff["dictionary_item_removed"].items() if v is not None and v != [] and v != {}
    }
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


@pytest.mark.asyncio
async def test_valid_search_tag_attribute_data(db: AsyncSession, attribute_with_normal_tag, auth_key, client) -> None:
    request_body = {"returnFormat": "json", "limit": 100, "value": attribute_with_normal_tag.value}
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
    assert False


@pytest.mark.asyncio
async def test_valid_event_view(
    db: AsyncSession, event, attribute_with_galaxy_cluster_one_tag, auth_key, client
) -> None:
    #    request_body = {"returnFormat": "json", "limit": 100, "value": attribute_with_galaxy_cluster_one_tag.value}
    request_body = {}
    path = f"/events/view/{event.id}"

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}
    assert False
