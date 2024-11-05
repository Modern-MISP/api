import random
import string

import pytest
import pytest_asyncio

from mmisp.tests.generators.model_generators.tag_generator import generate_tag
from mmisp.tests.generators.model_generators.taxonomy_generator import (
    generate_taxonomy,
    generate_taxonomy_entry,
    generate_taxonomy_predicate,
)


@pytest.mark.asyncio
async def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@pytest_asyncio.fixture
async def taxonomy(db):
    taxonomy = generate_taxonomy()

    db.add(taxonomy)
    await db.commit()
    await db.refresh(taxonomy)

    yield taxonomy

    await db.delete(taxonomy)
    await db.commit()


@pytest_asyncio.fixture
async def taxonomy_predicate(db, taxonomy):
    taxonomy_predicate = generate_taxonomy_predicate(taxonomy.id)

    db.add(taxonomy_predicate)
    await db.commit()
    await db.refresh(taxonomy_predicate)

    yield taxonomy_predicate

    await db.delete(taxonomy_predicate)
    await db.commit()


@pytest_asyncio.fixture
async def taxonomy_entry(db, taxonomy_predicate):
    taxonomy_entry = generate_taxonomy_entry(taxonomy_predicate.id)

    db.add(taxonomy_entry)
    await db.commit()
    await db.refresh(taxonomy_entry)

    yield taxonomy_entry

    await db.delete(taxonomy_entry)
    await db.commit()


@pytest.mark.asyncio
async def test_get_taxonomy_by_id(db, taxonomy, taxonomy_entry, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/taxonomies/{taxonomy.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["Taxonomy"]["id"] == 1


@pytest.mark.asyncio
async def test_get_taxonomy_by_non_existing_id(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/taxonomies/1000", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_taxonomy_expanded_by_id_with_tag(
    db, taxonomy, taxonomy_predicate, taxonomy_entry, site_admin_user_token, client
) -> None:
    tag = generate_tag()
    tag.name = taxonomy.namespace + ":" + taxonomy_predicate.value + '="' + taxonomy_entry.value + '"'

    db.add(tag)
    await db.commit()

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/taxonomies/taxonomy_tags/{taxonomy.id}", headers=headers)
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["id"] == taxonomy.id
    assert response_json["entries"][0]["tag"] == tag.name


@pytest.mark.asyncio
async def test_get_taxonomy_expanded_by_id_without_tag(
    db, taxonomy, taxonomy_predicate, taxonomy_entry, site_admin_user_token, client
) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/taxonomies/taxonomy_tags/{taxonomy.id}", headers=headers)
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["id"] == taxonomy.id


@pytest.mark.asyncio
async def test_get_taxonomy_expanded_by_invalid_id(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/taxonomies/taxonomy_tags/-1", headers=headers)
    response_json = response.json()
    assert response.status_code == 404
    assert response_json


@pytest.mark.asyncio
async def test_all_taxonomies(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/taxonomies", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_export_taxonomy(site_admin_user_token, taxonomy, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/taxonomies/export/{taxonomy.id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_enable_taxonomy(site_admin_user_token, taxonomy, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/taxonomies/enable/{taxonomy.id}", headers=headers, json={})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_disable_taxonomy(site_admin_user_token, taxonomy, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/taxonomies/disable/{taxonomy.id}", headers=headers, json={})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_taxonomy(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/taxonomies/update", headers=headers, json={})
    assert response.status_code == 200
