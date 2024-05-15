import random
import string

import pytest

from tests.environment import client
from tests.generators.model_generators.tag_generator import generate_tag
from tests.generators.model_generators.taxonomy_generator import (
    generate_taxonomy,
    generate_taxonomy_entry,
    generate_taxonomy_predicate,
)


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@pytest.fixture
def taxonomy(db):
    taxonomy = generate_taxonomy()

    db.add(taxonomy)
    db.commit()
    db.refresh(taxonomy)

    yield taxonomy

    db.delete(taxonomy)
    db.commit()


@pytest.fixture
def taxonomy_predicate(db, taxonomy):
    taxonomy_predicate = generate_taxonomy_predicate(taxonomy.id)

    db.add(taxonomy_predicate)
    db.commit()
    db.refresh(taxonomy_predicate)

    yield taxonomy_predicate

    db.delete(taxonomy_predicate)
    db.commit()


@pytest.fixture
def taxonomy_entry(db, taxonomy_predicate):
    taxonomy_entry = generate_taxonomy_entry(taxonomy_predicate.id)

    db.add(taxonomy_entry)
    db.commit()
    db.refresh(taxonomy_entry)

    yield taxonomy_entry

    db.delete(taxonomy_entry)
    db.commit()


def test_get_taxonomy_by_id(db, taxonomy, taxonomy_entry, site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/taxonomies/{taxonomy.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["Taxonomy"]["id"] == str(1)


def test_get_taxonomy_by_non_existing_id(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/taxonomies/1000", headers=headers)
    assert response.status_code == 404


def test_get_taxonomy_expanded_by_id_with_tag(
    db, taxonomy, taxonomy_predicate, taxonomy_entry, site_admin_user_token
) -> None:
    tag = generate_tag()
    tag.name = taxonomy.namespace + ":" + taxonomy_predicate.value + '="' + taxonomy_entry.value + '"'

    db.add(tag)
    db.commit()

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/taxonomies/taxonomy_tags/{taxonomy.id}", headers=headers)
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["id"] == str(taxonomy.id)
    assert response_json["entries"][0]["tag"] == tag.name


def test_get_taxonomy_expanded_by_id_without_tag(
    db, taxonomy, taxonomy_predicate, taxonomy_entry, site_admin_user_token
) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/taxonomies/taxonomy_tags/{taxonomy.id}", headers=headers)
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["id"] == str(taxonomy.id)


def test_get_taxonomy_expanded_by_invalid_id(db, site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/taxonomies/taxonomy_tags/-1", headers=headers)
    response_json = response.json()
    assert response.status_code == 404
    assert response_json


def test_all_taxonomies(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/taxonomies", headers=headers)
    assert response.status_code == 200


def test_export_taxonomy(site_admin_user_token, taxonomy) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/taxonomies/export/{taxonomy.id}", headers=headers)
    assert response.status_code == 200


def test_enable_taxonomy(site_admin_user_token, taxonomy) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/taxonomies/enable/{taxonomy.id}", headers=headers, json={})
    assert response.status_code == 200


def test_disable_taxonomy(site_admin_user_token, taxonomy) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/taxonomies/disable/{taxonomy.id}", headers=headers, json={})
    assert response.status_code == 200


def test_update_taxonomy(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/taxonomies/update", headers=headers, json={})
    assert response.status_code == 200
