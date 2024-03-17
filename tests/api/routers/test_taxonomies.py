import random
import string

from tests.environment import Session, client, environment
from tests.generators.model_generators.taxonomy_generator import (
    generate_taxonomy,
    generate_taxonomy_entry,
    generate_taxonomy_predicate,
)
from tests.generators.model_generators.tag_generator import generate_tag


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


class TestGetTaxonomyById:
    @staticmethod
    def test_get_taxonomy_by_id(db: Session) -> None:
        taxonomy = generate_taxonomy()

        db.add(taxonomy)
        db.flush()
        db.refresh(taxonomy)

        taxonomy_predicate = generate_taxonomy_predicate(taxonomy.id)

        db.add(taxonomy_predicate)
        db.flush()
        db.refresh(taxonomy_predicate)

        taxonomy_entry = generate_taxonomy_entry(taxonomy_predicate.id)

        db.add(taxonomy_entry)
        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/taxonomies/1", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == str(1)

    @staticmethod
    def test_get_taxonomy_by_non_existing_id() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/taxonomies/1000", headers=headers)
        assert response.status_code == 404

class TestGetTaxonomyExpanded:
    @staticmethod
    def test_get_taxonomy_expanded_by_id_with_tag(db: Session) -> None:
        taxonomy = generate_taxonomy()

        db.add(taxonomy)
        db.flush()
        db.refresh(taxonomy)

        taxonomy_predicate = generate_taxonomy_predicate(taxonomy.id)

        db.add(taxonomy_predicate)
        db.flush()
        db.refresh(taxonomy_predicate)

        taxonomy_entry = generate_taxonomy_entry(taxonomy_predicate.id)

        db.add(taxonomy_entry)
        db.commit()

        tag = generate_tag()
        tag.name = taxonomy.namespace + ":" + taxonomy_predicate.value + '="' + taxonomy_entry.value + '"'

        db.add(tag)
        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/taxonomies/taxonomy_tags/{taxonomy.id}", headers=headers)
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["id"] == str(taxonomy.id)
        assert response_json["entries"][0]["tag"] == tag.name

    @staticmethod
    def test_get_taxonomy_expanded_by_id_without_tag(db: Session) -> None:
        taxonomy = generate_taxonomy()

        db.add(taxonomy)
        db.flush()
        db.refresh(taxonomy)

        taxonomy_predicate = generate_taxonomy_predicate(taxonomy.id)

        db.add(taxonomy_predicate)
        db.flush()
        db.refresh(taxonomy_predicate)

        taxonomy_entry = generate_taxonomy_entry(taxonomy_predicate.id)

        db.add(taxonomy_entry)
        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/taxonomies/taxonomy_tags/{taxonomy.id}", headers=headers)
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["id"] == str(taxonomy.id)

    @staticmethod
    def test_get_taxonomy_expanded_by_invalid_id(db: Session) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/taxonomies/taxonomy_tags/-1", headers=headers)
        response_json = response.json()
        assert response.status_code == 404


class TestGetAllTaxonomies:
    @staticmethod
    def test_all_taxonomies() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/taxonomies", headers=headers)
        assert response.status_code == 200


class TestExportTaxonomy:
    @staticmethod
    def test_export_taxonomy() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/taxonomies/export/1", headers=headers)
        assert response.status_code == 200


class TestEnableTaxonomy:
    @staticmethod
    def test_enable_taxonomy() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/taxonomies/enable/1", headers=headers, json={})
        assert response.status_code == 200


class TestDisableTaxonomy:
    @staticmethod
    def test_disable_taxonomy() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/taxonomies/disable/1", headers=headers, json={})
        assert response.status_code == 200


class TestUpdateTaxonomy:
    @staticmethod
    def test_update_taxonomy() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/taxonomies/update", headers=headers, json={})
        assert response.status_code == 200
