import pytest
import sqlalchemy as sa
from icecream import ic
from sqlalchemy.orm import Session

from mmisp.api_schemas.attributes.get_describe_types_response import GetDescribeTypesAttributes
from mmisp.db.models.attribute import AttributeTag

from ...environment import client
from ...generators.model_generators.tag_generator import generate_tag


def test_add_attribute_valid_data(site_admin_user_token, event, db) -> None:
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

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/attributes/{event_id}", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Attribute"]["value"] == request_body["value"]
    assert response_json["Attribute"]["type"] == request_body["type"]
    assert response_json["Attribute"]["category"] == request_body["category"]
    assert response_json["Attribute"]["to_ids"] == request_body["to_ids"]
    assert response_json["Attribute"]["distribution"] == request_body["distribution"]
    assert response_json["Attribute"]["comment"] == request_body["comment"]
    assert response_json["Attribute"]["disable_correlation"] == request_body["disable_correlation"]
    assert response_json["Attribute"]["id"] is not None

    # need to remove attribute, so teardown works
    print(response_json["Attribute"]["id"])
    stmt = sa.sql.text("DELETE FROM attributes WHERE id=:id")
    #    stmt.bindparams(id=response_json["Attribute"]["id"])
    db.execute(stmt, {"id": response_json["Attribute"]["id"]})
    db.commit()


def test_add_attribute_invalid_event_id(site_admin_user_token) -> None:
    request_body = {
        "value": "1.2.3.4",
        "type": "ip-src",
        "category": "Network activity",
        "to_ids": True,
        "distribution": "1",
        "comment": "test comment",
        "disable_correlation": False,
    }
    headers = {"authorization": site_admin_user_token}
    response = client.post(
        "/attributes/0",
        json=request_body,
        headers=headers,
    )
    ic(response)
    assert response.status_code == 404


def test_add_attribute_invalid_data(db: Session, event, site_admin_user_token, sharing_group) -> None:
    request_body = {"value": "1.2.3.4", "type": "invalid"}

    event.sharing_group_id = sharing_group.id

    db.commit()

    event_id = event.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/attributes/{event_id}", json=request_body, headers=headers)
    ic(response.json())
    assert response.status_code == 422


# --- Test get attribute by id


def test_get_existing_attribute(
    db: Session,
    instance_org_two,
    site_admin_user_token,
    sharing_group,
    organisation,
    event,
    attribute,
    tag,
    attributetag,
) -> None:
    sharing_group_id = sharing_group.id
    event.sharing_group_id = sharing_group_id

    db.commit()

    event_id = event.id

    attribute.sharing_group_id = sharing_group_id

    assert tag.user_id == 1
    assert tag.org_id == 1

    attribute_id = attribute.id

    ic(attribute.asdict())

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/attributes/{attribute_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Attribute"]["id"] == str(attribute_id)
    assert response_json["Attribute"]["event_id"] == str(event_id)
    assert "id" in response_json["Attribute"]
    assert "event_id" in response_json["Attribute"]
    assert "object_id" in response_json["Attribute"]
    assert "object_relation" in response_json["Attribute"]
    assert "category" in response_json["Attribute"]
    assert "type" in response_json["Attribute"]
    assert "value" in response_json["Attribute"]
    assert "to_ids" in response_json["Attribute"]
    assert "uuid" in response_json["Attribute"]
    assert "timestamp" in response_json["Attribute"]
    assert "distribution" in response_json["Attribute"]
    assert "sharing_group_id" in response_json["Attribute"]
    assert "comment" in response_json["Attribute"]
    assert "deleted" in response_json["Attribute"]
    assert "disable_correlation" in response_json["Attribute"]
    assert "first_seen" in response_json["Attribute"]
    assert "last_seen" in response_json["Attribute"]
    assert "event_uuid" in response_json["Attribute"]
    assert "tag" in response_json["Attribute"]
    if len(response_json["Attribute"]["tag"]) > 0:
        print(response_json["Attribute"]["tag"])
        assert response_json["Attribute"]["tag"][0]["id"] == str(attributetag.id)


def test_get_invalid_or_non_existing_attribute(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/attributes/0", headers=headers)
    assert response.status_code == 404
    response = client.get("/attributes/invalid_id", headers=headers)
    assert response.status_code == 404


# --- Test edit attribute


def test_edit_existing_attribute(db: Session, site_admin_user_token, sharing_group, event, attribute) -> None:
    request_body = {
        "category": "Payload delivery",
        "value": "2.3.4.5",
        "to_ids": True,
        "distribution": "1",
        "comment": "new comment",
        "disable_correlation": False,
    }
    event.sharing_group_id = sharing_group.id
    db.commit()

    event_id = event.id

    attribute.sharing_group_id = sharing_group.id

    db.commit()

    attribute_id = attribute.id
    assert attribute.id is not None

    headers = {"authorization": site_admin_user_token}
    response = client.put(f"/attributes/{attribute_id}", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["Attribute"]["id"] == str(attribute_id)
    assert response_json["Attribute"]["event_id"] == str(event_id)
    assert "id" in response_json["Attribute"]
    assert "event_id" in response_json["Attribute"]
    assert "object_id" in response_json["Attribute"]
    assert "object_relation" in response_json["Attribute"]
    assert "category" in response_json["Attribute"]
    assert "type" in response_json["Attribute"]
    assert "value" in response_json["Attribute"]
    assert "to_ids" in response_json["Attribute"]
    assert "uuid" in response_json["Attribute"]
    assert "timestamp" in response_json["Attribute"]
    assert "distribution" in response_json["Attribute"]
    assert "sharing_group_id" in response_json["Attribute"]
    assert "comment" in response_json["Attribute"]
    assert "deleted" in response_json["Attribute"]
    assert "disable_correlation" in response_json["Attribute"]
    assert "first_seen" in response_json["Attribute"]
    assert "last_seen" in response_json["Attribute"]
    assert "tag" in response_json["Attribute"]


def test_edit_non_existing_attribute(site_admin_user_token) -> None:
    request_body = {
        "category": "Payload delivery",
        "value": "2.3.4.5",
        "to_ids": True,
        "distribution": "1",
        "comment": "new comment",
        "disable_correlation": False,
    }
    headers = {"authorization": site_admin_user_token}
    response = client.put("/attributes/0", json=request_body, headers=headers)
    assert response.status_code == 404
    response = client.put("/attributes/invalid_id", json=request_body, headers=headers)
    assert response.status_code == 404


# --- Test delete attribute by id
def test_delete_existing_attribute(
    db: Session, instance_org_two, site_admin_user_token, sharing_group, organisation, event, attribute
) -> None:
    event.sharing_group_id = sharing_group.id

    setattr(attribute, "sharing_group_id", sharing_group.id)

    db.commit()

    attribute_id = attribute.id

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/attributes/{attribute_id}", headers=headers)

    assert response.status_code == 200


def test_delete_invalid_or_non_existing_attribute(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete("/attributes/0", headers=headers)
    assert response.status_code == 404
    response = client.delete("/attributes/invalid_id", headers=headers)
    assert response.status_code == 404


# --- Test get all attributes


def test_get_all_attributes(
    db: Session, event, site_admin_user_token, sharing_group, organisation, attribute, attribute2
) -> None:
    event.sharing_group_id = sharing_group.id
    attribute.sharing_group_id = sharing_group.id
    attribute2.sharing_group_id = sharing_group.id

    db.commit()

    headers = {"authorization": site_admin_user_token}
    response = client.get("/attributes", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
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


# --- Test delete selected attribute(s)
def test_delete_selected_attributes_from_existing_event(
    db: Session, site_admin_user_token, sharing_group, event, attribute, attribute2
) -> None:
    request_body = {"id": "1 2 3", "allow_hard_delete": False}

    event_id = event.id
    setattr(event, "sharing_group_id", sharing_group.id)
    setattr(attribute, "sharing_group_id", sharing_group.id)
    setattr(attribute2, "sharing_group_id", sharing_group.id)

    db.commit()

    attribute_id = attribute.id
    attribute2_id = attribute2.id

    attribute_ids = str(attribute_id) + " " + str(attribute2_id)

    request_body["id"] = attribute_ids

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/attributes/deleteSelected/{event_id}", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    counter_of_selected_attributes = len(attribute_ids)
    if counter_of_selected_attributes == 1:
        assert response_json["message"] == "1 attribute deleted."
    else:
        assert response_json["message"] == "2 attributes deleted."
    assert response_json["url"] == f"/attributes/deleteSelected/{event_id}"


def test_valid_search_attribute_data(db: Session, event, site_admin_user_token, sharing_group) -> None:
    request_body = {"returnFormat": "json", "limit": 100}

    event.sharing_group_id = sharing_group.id
    db.commit()

    headers = {"authorization": site_admin_user_token}
    response = client.post("/attributes/restSearch", json=request_body, headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert "response" in response_json
    assert isinstance(response_json["response"]["Attribute"], list)


def test_invalid_search_attribute_data(site_admin_user_token) -> None:
    request_body = {"returnFormat": "invalid format"}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/attributes/restSearch", json=request_body, headers=headers)
    assert response.status_code == 404


# --- Test attribute statistics


def test_valid_parameters_attribute_statistics(site_admin_user_token) -> None:
    request_body = {"context": "category", "percentage": "1"}
    context = request_body["context"]
    percentage = request_body["percentage"]
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/attributes/attributeStatistics/{context}/{percentage}", headers=headers)
    assert response.status_code == 200
    response_json = response.json()

    if context == "category":
        for category in GetDescribeTypesAttributes().categories:
            assert category in response_json
    else:
        for type in GetDescribeTypesAttributes().types:
            assert type in response_json
    if percentage == 1:
        for item in response_json:
            assert "%" in item


def test_invalid_parameters_attribute_statistics(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/attributes/attributeStatistics/invalid_context/0", headers=headers)
    assert response.status_code == 422
    response = client.get("/attributes/attributeStatistics/type/non_boolean", headers=headers)
    assert response.status_code == 422


# --- Test attribute describe types


def test_attribute_describe_types(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/attributes/describeTypes", headers=headers)
    assert response.status_code == 200


# --- Test restore attribute


def test_restore_existing_attribute(db: Session, site_admin_user_token, sharing_group, event, attribute) -> None:
    event.sharing_group_id = sharing_group.id

    db.add(event)
    db.commit()
    db.refresh(event)

    attribute.sharing_group_id = sharing_group.id

    db.commit()

    attribute_id = attribute.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/attributes/restore/{attribute_id}", headers=headers)
    assert response.status_code == 200


def test_restore_invalid_attribute(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/attributes/restore/0", headers=headers)
    assert response.status_code == 404
    response = client.post("/attributes/restore/invalid_id", headers=headers)
    assert response.status_code == 404


# --- Test adding a tag


def test_add_existing_tag_to_attribute(db: Session, site_admin_user_token, sharing_group, event, attribute) -> None:
    event.sharing_group_id = sharing_group.id

    setattr(attribute, "sharing_group_id", sharing_group.id)

    db.commit()

    attribute_id = attribute.id

    tag = generate_tag()
    setattr(tag, "user_id", 1)
    setattr(tag, "org_id", 1)

    db.add(tag)
    db.commit()
    db.refresh(tag)

    tag_id = tag.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(
        f"/attributes/addTag/{attribute_id}/{tag_id}/local:1",
        headers=headers,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["success"] == "Tag added"
    assert response_json["check_publish"]


def test_add_invalid_or_non_existing_tag_to_attribute(
    db: Session, site_admin_user_token, event, sharing_group, attribute
) -> None:
    event.sharing_group_id = sharing_group.id
    attribute.sharing_group_id = sharing_group.id

    db.commit()

    attribute_id = attribute.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(
        f"/attributes/addTag/{attribute_id}/0/local:0",
        headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"] is False
    response = client.post(
        f"/attributes/addTag/{attribute_id}/invalid_id/local:1",
        headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"] is False


@pytest.fixture
def attributetag(attribute, event, tag, db):
    attribute_tag = AttributeTag(attribute_id=attribute.id, event_id=event.id, tag_id=tag.id, local=False)

    db.add(attribute_tag)
    db.commit()

    yield attribute_tag

    db.delete(attribute_tag)
    db.commit


def test_remove_existing_tag_from_attribute(
    db: Session, site_admin_user_token, sharing_group, event, attribute, tag, attributetag
) -> None:
    event.sharing_group_id = sharing_group.id
    db.commit()

    attribute.sharing_group_id = sharing_group.id
    db.commit()

    attribute_id = attribute.id

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/attributes/removeTag/{attribute_id}/{tag.id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["success"] == "Tag removed"
