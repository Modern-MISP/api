import random
from typing import Any, Dict

import pytest
from sqlalchemy.orm import Session

from mmisp.db.database import get_db
from mmisp.db.models.tag import Tag
from tests.api.helpers.tags_helper import (
    add_tags,
    generate_invalid_tag_data,
    generate_valid_required_tag_data,
    generate_valid_tag_data,
    get_invalid_tags,
    get_non_existing_tags,
    random_string,
    random_string_with_punctuation,
    remove_tags,
)
from tests.environment import client, environment


@pytest.fixture(
    params=[
        generate_valid_tag_data().dict(),
        generate_valid_tag_data().dict(),
        generate_valid_tag_data().dict(),
        generate_valid_required_tag_data().dict(),
        generate_valid_required_tag_data().dict(),
        generate_valid_required_tag_data().dict(),
    ]
)
def tag_data(request: Any) -> Dict[str, Any]:
    return request.param


@pytest.fixture(
    params=[
        generate_invalid_tag_data(),
        generate_invalid_tag_data(),
        generate_invalid_tag_data(),
    ]
)
def invalid_tag_data(request: Any) -> Dict[str, Any]:
    return request.param


class TestAddTag:
    @staticmethod
    def test_add_tag(tag_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/tags/", json=tag_data, headers=headers)
        assert response.status_code == 201

        remove_tags([response.json()["id"]])

    @staticmethod
    def test_add_tag_invalid_data(invalid_tag_data: Any) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/tags/", json=invalid_tag_data, headers=headers)
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "field required" or "none is not an allowed value"

    @staticmethod
    def test_tag_response_format(tag_data: Dict[str, Any]) -> None:
        tag_data.pop("name")
        tag_data["name"] = random_string()
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/tags/", json=tag_data, headers=headers)
        json = response.json()
        json["name"] == tag_data["name"]

        remove_tags([response.json()["id"]])


class TestViewTag:
    @staticmethod
    def test_view_tag() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        tags = add_tags()
        non_existing_tags = get_non_existing_tags()
        invalid_tags = get_invalid_tags()

        for tag in tags:
            response = client.get(f"/tags/{tag}", headers=headers)
            assert response.status_code == 200

        for non_existing_tag in non_existing_tags:
            response = client.get(f"/tags/{non_existing_tag}", headers=headers)
            assert response.status_code == 404

        for invalid_tag in invalid_tags:
            response = client.get(f"/tags/{invalid_tag}", headers=headers)
            assert response.status_code == 404

        remove_tags(tags)

    @staticmethod
    def test_view_tag_response_format() -> None:
        headers = {"authorization": environment.site_admin_user_token}

        tag = add_tags(1)

        response = client.get(f"tags/{tag[0]}", headers=headers)
        assert response.status_code == 200
        json = response.json()
        assert json["id"] == str(tag[0])

        remove_tags(tag)


# TODO: Need implementation of Taxonomies and TaxonomyPredicates
@staticmethod
class TestSearchTagByTagSearchTerm:
    def test_search_tag() -> None:
        db: Session = get_db()
        headers = {"authorization": environment.site_admin_user_token}

        tags = add_tags()

        for tag in tags:
            tag_name = db.get(Tag, tag).name
            substring_start = random.randint(0, len(tag_name) - 1)
            substring_end = random.randint(substring_start + 1, len(tag_name))
            substring = tag_name[substring_start:substring_end]
            response = client.get(f"/tags/search/{substring}", headers=headers)
            assert response.status_code == 200

        name = random_string_with_punctuation(4)
        response = client.get(f"/tags/search/{name}", headers=headers)
        assert response.status_code == 200
        json = response.json()
        assert isinstance(json["root"], list)
        assert len(json["root"]) == 0

        remove_tags(tags)

    @staticmethod
    def test_search_tag_response_format() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        db: Session = get_db()
        tag = add_tags(1)
        tag_name = db.get(Tag, tag[0]).name
        substring_start = random.randint(0, len(tag_name) - 1)
        substring_end = random.randint(substring_start + 1, len(tag_name))
        substring = tag_name[substring_start:substring_end]

        response = client.get(f"tags/search/{substring}", headers=headers)
        assert response.status_code == 200
        json = response.json()
        assert isinstance(json["root"], list)

        remove_tags(tag)


class TestEditTag:
    @staticmethod
    def test_edit_tag(tag_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}

        tags = add_tags()
        tag_data.pop("name")
        for tag in tags:
            response = client.put(f"/tags/{tag}", json=tag_data, headers=headers)
            assert response.status_code == 200

        non_existing_tags = get_non_existing_tags()
        for non_existing_tag in non_existing_tags:
            response = client.put(f"/tags/{non_existing_tag}", json=tag_data, headers=headers)
            assert response.status_code == 404

        invalid_tags = get_invalid_tags()
        for invalid_tag in invalid_tags:
            response = client.put(f"/tags/{invalid_tag}", json=tag_data, headers=headers)
            assert response.status_code == 404

        remove_tags(tags)

    @staticmethod
    def test_edit_tag_same_name() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        db: Session = get_db()

        tags = add_tags(2)
        name = db.get(Tag, tags[0]).name

        response = client.put(f"/tags/{tags[0]}", json={"name": name}, headers=headers)
        assert response.status_code == 400

        remove_tags(tags)

    @staticmethod
    def test_edit_tag_response_format(tag_data: Dict[str, Any]) -> None:
        tag = add_tags(1)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.put(f"tags/{tag[0]}", json=tag_data, headers=headers)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        json = response.json()
        print(json)
        assert json["id"] == str(tag[0])

        remove_tags(tag)


class TestDeleteTag:
    @staticmethod
    def test_delete_tag() -> None:
        headers = {"authorization": environment.site_admin_user_token}

        tags = add_tags()

        for tag in tags:
            response = client.delete(f"/tags/{tag}", headers=headers)
            assert response.status_code == 200

        non_existing_tags = get_non_existing_tags()
        for non_existing_tag in non_existing_tags:
            response = client.delete(f"/tags/{non_existing_tag}", headers=headers)
            assert response.status_code == 404

        invalid_tags = get_invalid_tags()
        for invalid_tag in invalid_tags:
            response = client.delete(f"/tags/{invalid_tag}", headers=headers)
            assert response.status_code == 404

    @staticmethod
    def test_edit_delete_response_format() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        tag = add_tags(1)
        response = client.delete(f"tags/{tag[0]}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        json = response.json()
        json["name"] == "Tag deleted."


class TestGetAllTags:
    @staticmethod
    def test_get_all_tags() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/tags/", headers=headers)
        assert response.status_code == 200

    @staticmethod
    def test_test_get_all_tags_response_format() -> None:
        tags = add_tags(1)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/tags/", headers=headers)
        assert response.headers["Content-Type"] == "application/json"

        json = response.json()

        assert isinstance(json["tag"], list)

        assert "tag" in json
        for tag_wrapper in json["tag"]:
            assert "id" in tag_wrapper
            assert "name" in tag_wrapper
            assert "colour" in tag_wrapper
            assert "exportable" in tag_wrapper

        remove_tags(tags)
