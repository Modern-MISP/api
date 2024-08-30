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
from mmisp.util.uuid import uuid


def galaxy_tag_name_from_uuid(galaxy_cluster_uuid):
    return f'misp-galaxy:test="{galaxy_cluster_uuid}"'


@pytest.fixture
def galaxy_cluster_collection_uuid():
    return uuid()


@pytest.fixture
def galaxy_cluster_one_uuid():
    return uuid()


@pytest.fixture
def galaxy_cluster_two_uuid():
    return uuid()


@pytest_asyncio.fixture
async def galaxy(db, instance_owner_org, galaxy_cluster_one_uuid, galaxy_cluster_two_uuid):
    galaxy = Galaxy(
        namespace="misp",
        name="test galaxy",
        type="test galaxy type",
        description="test",
        version="1",
        kill_chain_order=None,
        uuid=uuid(),
        enabled=True,
        local_only=False,
    )

    db.add(galaxy)
    await db.commit()
    await db.refresh(galaxy)

    galaxy_cluster = GalaxyCluster(
        uuid=galaxy_cluster_one_uuid,
        collection_uuid="",
        type="test galaxy type",
        value="test",
        tag_name=galaxy_tag_name_from_uuid(galaxy_cluster_one_uuid),
        description="test",
        galaxy_id=galaxy.id,
        source="me",
        authors='["Konstantin Zangerle", "Test Writer"]',
        version=1,
        distribution=3,
        sharing_group_id=None,
        org_id=instance_owner_org.id,
        orgc_id=instance_owner_org.id,
        default=0,
        locked=0,
        extends_uuid=None,
        extends_version=None,
        published=True,
        deleted=False,
    )
    galaxy_cluster2 = GalaxyCluster(
        uuid=galaxy_cluster_two_uuid,
        collection_uuid="",
        type="test galaxy type",
        value="test",
        tag_name=galaxy_tag_name_from_uuid(galaxy_cluster_two_uuid),
        description="test",
        galaxy_id=galaxy.id,
        source="me",
        authors='["Konstantin Zangerle", "Test Writer"]',
        version=1,
        distribution=3,
        sharing_group_id=None,
        org_id=instance_owner_org.id,
        orgc_id=instance_owner_org.id,
        default=0,
        locked=0,
        extends_uuid=None,
        extends_version=None,
        published=True,
        deleted=False,
    )

    db.add(galaxy_cluster)
    db.add(galaxy_cluster2)

    await db.commit()
    await db.refresh(galaxy_cluster)
    await db.refresh(galaxy_cluster2)

    galaxy_element = GalaxyElement(
        galaxy_cluster_id=galaxy_cluster.id, key="refs", value="http://test-one-one.example.com"
    )
    galaxy_element2 = GalaxyElement(
        galaxy_cluster_id=galaxy_cluster.id, key="refs", value="http://test-one-two.example.com"
    )

    galaxy_element21 = GalaxyElement(
        galaxy_cluster_id=galaxy_cluster2.id, key="refs", value="http://test-two-one.example.com"
    )
    galaxy_element22 = GalaxyElement(
        galaxy_cluster_id=galaxy_cluster2.id, key="refs", value="http://test-two-two.example.com"
    )

    db.add(galaxy_element)
    db.add(galaxy_element2)

    db.add(galaxy_element21)
    db.add(galaxy_element22)

    await db.commit()

    yield {
        "galaxy": galaxy,
        "galaxy_cluster": galaxy_cluster,
        "galaxy_cluster2": galaxy_cluster2,
        "galaxy_element": galaxy_element,
        "galaxy_element2": galaxy_element2,
        "galaxy_element21": galaxy_element21,
        "galaxy_element22": galaxy_element22,
    }

    await db.delete(galaxy_element22)
    await db.delete(galaxy_element21)
    await db.delete(galaxy_element2)
    await db.delete(galaxy_element)
    await db.delete(galaxy_cluster2)
    await db.delete(galaxy_cluster)
    await db.delete(galaxy)
    await db.commit()


@pytest_asyncio.fixture()
async def galaxy_cluster_one_tag(db, galaxy_cluster_one_uuid):
    tag = Tag(
        name=galaxy_tag_name_from_uuid(galaxy_cluster_one_uuid),
        colour="#123456",
        exportable=True,
        hide_tag=False,
        numerical_value=None,
        local_only=False,
        user_id=0,
        org_id=0,
        is_galaxy=True,
        is_custom_galaxy=True,
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    yield tag

    await db.delete(tag)
    await db.commit()


@pytest_asyncio.fixture()
async def galaxy_cluster_two_tag(db):
    tag = Tag(
        name='misp-galaxy:test="two"',
        colour="#123456",
        exportable=True,
        hide_tag=False,
        numerical_value=None,
        local_only=False,
        user_id=0,
        org_id=0,
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
async def attribute_with_galaxy_cluster_one_tag(db, attribute, galaxy_cluster_one_tag, galaxy):
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

    kwargs = {"headers": headers}
    if http_method != "get":
        kwargs["json"] = body

    call = getattr(client, http_method)
    response = call(path, **kwargs)
    response_json = response.json()
    response_json_in_legacy = to_legacy_format(response_json)

    call = getattr(httpx, http_method)
    legacy_response = call(f"http://misp-core{path}", **kwargs)
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

    # get_legacy_modern_diff("get", f"/galaxies/view/{galaxy.id}", request_body, auth_key, client)
    # get_legacy_modern_diff("get", f"/galaxy_clusters/view/{galaxy_cluster_one.id}", request_body, auth_key, client)
    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}
    assert False
