import random
from typing import Any, Dict

import pytest
from sqlalchemy.orm import Session

from mmisp.db.database import get_db
from mmisp.db.models.tag import Tag

from ...environment import client, environment
from ...generators.tag_generator import (
    generate_invalid_tag_data,
    generate_tags,
    generate_valid_required_tag_data,
    generate_valid_tag_data,
    get_invalid_tags,
    get_non_existing_tags,
    random_string_with_punctuation,
    remove_tags,
)


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


# --- Test cases ---


class TestAddTag:
    def test_add_tag(self: "TestAddTag", tag_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/tags/", json=tag_data, headers=headers)
        assert response.status_code == 201

        remove_tags([int(response.json()["id"])])

    def test_add_tag_invalid_data(self: "TestAddTag", invalid_tag_data: Any) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/tags/", json=invalid_tag_data, headers=headers)
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "field required" or "none is not an allowed value"

    def test_tag_response_format(self: "TestAddTag", tag_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/tags/", json=tag_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"

        remove_tags([int(response.json()["id"])])

    def test_add_tag_authorization(self: "TestAddTag", tag_data: Dict[str, Any]) -> None:
        headers = {"authorization": ""}
        response = client.post("/tags/", json=tag_data, headers=headers)
        assert response.status_code == 401


class TestViewTag:
    def test_view_tag(self: "TestViewTag") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        tags = generate_tags()
        non_existing_tags = get_non_existing_tags()
        invalid_tags = get_invalid_tags()

        for tag in tags:
            response = client.get(f"/tags/{tag}", headers=headers)
            assert response.status_code == 200

        for non_existing_tag in non_existing_tags:
            response = client.get(f"/tags/{non_existing_tag}", headers=headers)
            assert response.status_code == 404

        # TODO: check_existencce_and_raise expand for HTTP_Code 422
        #    by checking if value is given parameter (str instead of int)
        for invalid_tag in invalid_tags:
            response = client.get(f"/tags/{invalid_tag}", headers=headers)
            assert response.status_code == 404

        remove_tags(tags)

    def test_view_tag_response_format(self: "TestViewTag") -> None:
        headers = {"authorization": environment.site_admin_user_token}

        tag = generate_tags(1)

        response = client.get(f"tags/{tag}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"

        remove_tags(tag)

    def test_view_tag_authorization(self: "TestViewTag") -> None:
        headers = {"authorization": ""}

        tag = generate_tags(1)

        response = client.get(f"/tags/{tag}", headers=headers)
        assert response.status_code == 401

        remove_tags(tag)


# TODO: Need implementation of Taxonomies and TaxonomyPredicates
class TestSearchTagByTagSearchTerm:
    def test_search_tag(self: "TestSearchTagByTagSearchTerm") -> None:
        db: Session = get_db()
        headers = {"authorization": environment.site_admin_user_token}

        tags = generate_tags()

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
        # TODO: Check body is empty

        remove_tags(tags)

    # TODO: format
    def test_search_tag_response_format(self: "TestSearchTagByTagSearchTerm") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        db: Session = get_db()
        tag = generate_tags(1)
        tag_name = db.get(Tag, tag).name
        substring_start = random.randint(0, len(tag_name) - 1)
        substring_end = random.randint(substring_start + 1, len(tag_name))
        substring = tag_name[substring_start:substring_end]

        response = client.get(f"tags/search/{substring}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"

        remove_tags(tag)

    def test_search_tag_authorization(self: "TestSearchTagByTagSearchTerm") -> None:
        headers = {"authorization": ""}
        db: Session = get_db()
        tag = generate_tags(1)
        tag_name = db.get(Tag, tag).name
        substring_start = random.randint(0, len(tag_name) - 1)
        substring_end = random.randint(substring_start + 1, len(tag_name))
        substring = tag_name[substring_start:substring_end]

        response = client.get(f"/tags/search/{substring}", headers=headers)
        assert response.status_code == 401

        remove_tags(tag)


class TestEditTag:
    def test_edit_tag(self: "TestEditTag", tag_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}

        tags = generate_tags()
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

    def test_edit_tag_same_name(self: "TestEditTag") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        db: Session = get_db()

        tags = generate_tags(2)
        name = db.get(Tag, tags[0]).name

        response = client.put(f"/tags/{tags[0]}", json={"name": name}, headers=headers)
        assert response.status_code == 400

        remove_tags(tags)

    # TODO: format
    def test_edit_tag_response_format(self: "TestEditTag", tag_data: Dict[str, Any]) -> None:
        headers = {"authorization": environment.site_admin_user_token}

        tag = generate_tags(1)

        response = client.put(f"tags/{tag}", json=tag_data, headers=headers)
        assert response.headers["Content-Type"] == "application/json"

        remove_tags(tag)

    def test_edit_tag_authorization(self: "TestEditTag", tag_data: Dict[str, Any]) -> None:
        headers = {"authorization": ""}

        tag = generate_tags(1)

        response = client.put(f"/tags/{tag}", json=tag_data, headers=headers)
        assert response.status_code == 401

        remove_tags(tag)


class TestDeleteTag:
    def test_delete_tag(self: "TestDeleteTag") -> None:
        headers = {"authorization": environment.site_admin_user_token}

        tags = generate_tags()

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

    # TODO: format
    def test_edit_delete_response_format(self: "TestDeleteTag") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        tag = generate_tags(1)
        response = client.delete(f"tags/{tag}", headers=headers)
        assert response.headers["Content-Type"] == "application/json"

    def test_delete_tag_authorization(self: "TestDeleteTag") -> None:
        headers = {"authorization": ""}
        tag = generate_tags(1)
        response = client.delete(f"/tags/{tag}", headers=headers)
        assert response.status_code == 401
        remove_tags([tag])


class TestGetAllTags:
    def test_get_all_tags(self: "TestGetAllTags") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/tags/", headers=headers)
        assert response.status_code == 200

    def test_test_get_all_tags_response_format(self: "TestGetAllTags") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/tags/", headers=headers)
        assert response.headers["Content-Type"] == "application/json"

        response_data = response.json()

        assert isinstance(response_data["tag"], list)

        # Test all required fields
        assert "tag" in response_data
        for tag_wrapper in response_data["tag"]:
            assert "id" in tag_wrapper
            assert "name" in tag_wrapper
            assert "colour" in tag_wrapper
            assert "exportable" in tag_wrapper

    def test_get_all_tags_authorization(self: "TestGetAllTags") -> None:
        headers = {"authorization": ""}
        response = client.get("/tags/", headers=headers)
        assert response.status_code == 401
