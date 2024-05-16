import random
from typing import Any, Dict

import pytest
from sqlalchemy.orm import Session

from mmisp.db.models.tag import Tag
from tests.api.helpers.tags_helper import (
    generate_invalid_tag_data,
    generate_valid_required_tag_data,
    generate_valid_tag_data,
    get_invalid_tags,
    get_non_existing_tags,
    random_string_with_punctuation,
    remove_tags,
)
from tests.environment import client
from tests.generators.model_generators.organisation_generator import generate_organisation


@pytest.fixture(
    params=[
        generate_valid_tag_data,
        generate_valid_required_tag_data,
    ]
)
def tag_data(request: Any, organisation, site_admin_user) -> Dict[str, Any]:
    return request.param(organisation, site_admin_user).dict()


@pytest.fixture
def add_tags(db, site_admin_user):
    tags = []
    orgs = []

    def create_tags(amount=5):
        for _ in range(amount):
            org = generate_organisation()
            db.add(org)
            db.commit()
            orgs.append(org)
            new_tag = Tag(**generate_valid_tag_data(org, site_admin_user).dict())
            tags.append(new_tag)
            db.add(new_tag)
            db.commit()
        return [x.id for x in tags]

    yield create_tags

    for x in tags:
        db.delete(x)
    for x in orgs:
        db.delete(x)
    db.commit()


@pytest.fixture(
    params=[
        generate_invalid_tag_data(),
        generate_invalid_tag_data(),
    ]
)
def invalid_tag_data(request: Any) -> Dict[str, Any]:
    return request.param


def test_add_tag(tag_data: Dict[str, Any], site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags", json=tag_data, headers=headers)
    assert response.status_code == 201

    remove_tags([response.json()["Tag"]["id"]])


def test_add_tag_deprecated(tag_data: Dict[str, Any], site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags/add", json=tag_data, headers=headers)
    assert response.status_code == 201

    remove_tags([response.json()["Tag"]["id"]])


def test_add_tag_with_existing_name(db: Session, add_tags, site_admin_user_token) -> None:
    tag_id = add_tags(1)
    tag_data = generate_valid_required_tag_data()
    tag_data.name = db.get(Tag, tag_id[0]).name
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags", json=tag_data.dict(), headers=headers)
    assert response.status_code == 403

    remove_tags(tag_id)


def test_add_tag_with_existing_name_deprecated(db: Session, add_tags, site_admin_user_token) -> None:
    tag_id = add_tags(1)
    tag_data = generate_valid_required_tag_data()
    tag_data.name = db.get(Tag, tag_id[0]).name
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags/add", json=tag_data.dict(), headers=headers)
    assert response.status_code == 403

    remove_tags(tag_id)


def test_add_tag_with_invalid_colour(site_admin_user_token) -> None:
    tag_data = generate_valid_required_tag_data()
    tag_data.colour = "#12345,"
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags", json=tag_data.dict(), headers=headers)
    assert response.status_code == 400


def test_add_tag_invalid_data(invalid_tag_data: Any, site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags", json=invalid_tag_data, headers=headers)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "field required" or "none is not an allowed value"


def test_add_tag_response_format(tag_data: Dict[str, Any], site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags", json=tag_data, headers=headers)

    json = response.json()
    json["Tag"]["name"] == tag_data["name"]
    json["Tag"]["colour"] == tag_data["colour"]
    json["Tag"]["exportable"] == tag_data["exportable"]

    remove_tags([response.json()["Tag"]["id"]])


def test_add_tag_response_format_deprecated(tag_data: Dict[str, Any], site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/tags/add", json=tag_data, headers=headers)

    json = response.json()
    json["Tag"]["name"] == tag_data["name"]
    json["Tag"]["colour"] == tag_data["colour"]
    json["Tag"]["exportable"] == tag_data["exportable"]

    remove_tags([response.json()["Tag"]["id"]])


def test_view_tag(add_tags, site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    tags = add_tags(5)
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
        assert response.status_code == 422

    remove_tags(tags)


def test_view_tag_deprecated(add_tags, site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    tags = add_tags()
    non_existing_tags = get_non_existing_tags()
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

    remove_tags(tags)


def test_view_tag_response_format(site_admin_user_token, add_tags) -> None:
    headers = {"authorization": site_admin_user_token}

    tag = add_tags(1)

    response = client.get(f"tags/{tag[0]}", headers=headers)
    assert response.status_code == 200
    json = response.json()
    assert json["id"] == str(tag[0])

    remove_tags(tag)


def test_view_tag_response_format_deprecated(site_admin_user_token, add_tags) -> None:
    headers = {"authorization": site_admin_user_token}

    tag = add_tags(1)

    response = client.get(f"tags/view/{tag[0]}", headers=headers)
    assert response.status_code == 200
    json = response.json()
    assert json["id"] == str(tag[0])

    remove_tags(tag)


def test_search_tag(db: Session, site_admin_user_token, add_tags) -> None:
    headers = {"authorization": site_admin_user_token}

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
    assert isinstance(json["response"], list)
    assert len(json["response"]) == 0

    remove_tags(tags)


def test_search_tag_response_format(db: Session, site_admin_user_token, add_tags) -> None:
    headers = {"authorization": site_admin_user_token}
    tag = add_tags(1)
    tag_name = db.get(Tag, tag[0]).name
    substring_start = random.randint(0, len(tag_name) - 1)
    substring_end = random.randint(substring_start + 1, len(tag_name))
    substring = tag_name[substring_start:substring_end]

    response = client.get(f"tags/search/{substring}", headers=headers)
    assert response.status_code == 200
    json = response.json()
    assert isinstance(json["response"], list)

    remove_tags(tag)


def test_edit_tag(tag_data: Dict[str, Any], site_admin_user_token, add_tags) -> None:
    headers = {"authorization": site_admin_user_token}

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
        assert response.status_code == 422

    remove_tags(tags)


def test_edit_tag_deprecated(tag_data: Dict[str, Any], site_admin_user_token, add_tags) -> None:
    headers = {"authorization": site_admin_user_token}

    tags = add_tags(1)
    for tag in tags:
        response = client.post(f"/tags/edit/{tag}", json=tag_data, headers=headers)
        assert response.status_code == 200

    non_existing_tags = get_non_existing_tags()
    for non_existing_tag in non_existing_tags:
        response = client.post(f"/tags/edit/{non_existing_tag}", json=tag_data, headers=headers)
        assert response.status_code == 404

    invalid_tags = get_invalid_tags()
    for invalid_tag in invalid_tags:
        response = client.post(f"/tags/edit/{invalid_tag}", json=tag_data, headers=headers)
        assert response.status_code == 422

    remove_tags(tags)


def test_edit_tag_same_name(db: Session, site_admin_user_token, add_tags) -> None:
    headers = {"authorization": site_admin_user_token}

    tags = add_tags(2)
    name = db.get(Tag, tags[0]).name

    response = client.put(f"/tags/{tags[1]}", json={"name": name}, headers=headers)
    assert response.status_code == 403

    remove_tags(tags)


def test_edit_tag_same_name_deprecated(db: Session, site_admin_user_token, add_tags) -> None:
    headers = {"authorization": site_admin_user_token}

    tags = add_tags(2)
    name = db.get(Tag, tags[0]).name

    response = client.post(f"/tags/edit/{tags[1]}", json={"name": name}, headers=headers)
    assert response.status_code == 403

    remove_tags(tags)


def test_edit_tag_response_format(tag_data: Dict[str, Any], site_admin_user_token, add_tags) -> None:
    tag = add_tags(1)

    headers = {"authorization": site_admin_user_token}
    response = client.put(f"tags/{tag[0]}", json=tag_data, headers=headers)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    json = response.json()
    print(json)
    assert json["Tag"]["id"] == str(tag[0])

    remove_tags(tag)


def test_delete_tag(site_admin_user_token, add_tags) -> None:
    headers = {"authorization": site_admin_user_token}

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
        assert response.status_code == 422


def test_delete_tag_deprecated(site_admin_user_token, add_tags) -> None:
    headers = {"authorization": site_admin_user_token}

    tags = add_tags()

    for tag in tags:
        response = client.post(f"/tags/delete/{tag}", headers=headers)
        assert response.status_code == 200


def test_edit_delete_response_format(site_admin_user_token, add_tags) -> None:
    headers = {"authorization": site_admin_user_token}
    tag = add_tags(1)
    response = client.delete(f"tags/{tag[0]}", headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    json = response.json()
    json["name"] == "Tag deleted."


def test_edit_delete_response_format_deprecated(site_admin_user_token, add_tags) -> None:
    headers = {"authorization": site_admin_user_token}
    tag = add_tags(1)
    response = client.post(f"tags/delete/{tag[0]}", headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    json = response.json()
    json["name"] == "Tag deleted."


def test_get_all_tags(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/tags", headers=headers)
    assert response.status_code == 200


def test_get_all_tags_response_format(site_admin_user_token, add_tags) -> None:
    tags = add_tags(1)

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

    remove_tags(tags)
