from sqlalchemy.orm import Session

from mmisp.api_schemas.attributes.get_describe_types_response import GetDescribeTypesAttributes
from mmisp.db.models.attribute import AttributeTag

from ...environment import client, environment
from ...generators.model_generators.attribute_generator import generate_attribute
from ...generators.model_generators.event_generator import generate_event
from ...generators.model_generators.organisation_generator import generate_organisation
from ...generators.model_generators.sharing_group_generator import generate_sharing_group
from ...generators.model_generators.tag_generator import generate_tag

# --- Test cases ---


# --- Test add attribute


class TestAddAttribute:
    @staticmethod
    def test_add_attribute_valid_data(db: Session) -> None:
        request_body = {
            "value": "1.2.3.4",
            "type": "ip-src",
            "category": "Network activity",
            "to_ids": True,
            "distribution": "1",
            "comment": "test comment",
            "disable_correlation": False,
        }

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)
        setattr(event, "sharing_group_id", sharing_group.id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
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

    @staticmethod
    def test_add_attribute_invalid_event_id() -> None:
        request_body = {
            "value": "1.2.3.4",
            "type": "ip-src",
            "category": "Network activity",
            "to_ids": True,
            "distribution": "1",
            "comment": "test comment",
            "disable_correlation": False,
        }
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            "/attributes/0",
            json=request_body,
            headers=headers,
        )
        assert response.status_code == 404

    @staticmethod
    def test_add_attribute_invalid_data(db: Session) -> None:
        request_body = {"value": "1.2.3.4", "type": "invalid type"}
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)
        setattr(event, "sharing_group_id", sharing_group.id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/attributes/{event_id}", json=request_body, headers=headers)
        assert response.status_code == 403


# --- Test get attribute by id


class TestGetAttributeDetails:
    @staticmethod
    def test_get_existing_attribute(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        organisation = generate_organisation()

        db.add_all([sharing_group, organisation])
        db.commit()
        db.refresh(sharing_group)
        db.refresh(organisation)

        sharing_group_id = sharing_group.id
        org_id = organisation.id

        event = generate_event()
        event.org_id = org_id
        event.orgc_id = org_id
        event.sharing_group_id = sharing_group_id

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        attribute = generate_attribute()
        attribute.event_id = event_id
        attribute.sharing_group_id = sharing_group_id

        tag = generate_tag()
        tag.user_id = 1
        tag.org_id = 1

        db.add_all([attribute, tag])
        db.commit()
        db.refresh(attribute)
        db.refresh(tag)

        attribute_id = attribute.id
        tag_id = tag.id

        add_attribute_tag_body = AttributeTag(attribute_id=attribute_id, event_id=event_id, tag_id=tag_id, local=False)

        db.add(add_attribute_tag_body)
        db.commit()
        db.refresh(add_attribute_tag_body)

        headers = {"authorization": environment.site_admin_user_token}
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
            assert response_json["Attribute"]["tag"][0]["id"] == str(tag_id)

    @staticmethod
    def test_get_invalid_or_non_existing_attribute() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/attributes/0", headers=headers)
        assert response.status_code == 404
        response = client.get("/attributes/invalid_id", headers=headers)
        assert response.status_code == 404


# --- Test edit attribute


class TestEditAttribute:
    @staticmethod
    def test_edit_existing_attribute(db: Session) -> None:
        request_body = {
            "category": "Payload delivery",
            "value": "2.3.4.5",
            "to_ids": True,
            "distribution": "1",
            "comment": "new comment",
            "disable_correlation": False,
        }
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)
        setattr(event, "sharing_group_id", sharing_group.id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        attribute = generate_attribute()
        setattr(attribute, "event_id", event_id)
        setattr(attribute, "sharing_group_id", sharing_group.id)

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        attribute_id = attribute.id

        headers = {"authorization": environment.site_admin_user_token}
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

    @staticmethod
    def test_edit_non_existing_attribute() -> None:
        request_body = {
            "category": "Payload delivery",
            "value": "2.3.4.5",
            "to_ids": True,
            "distribution": "1",
            "comment": "new comment",
            "disable_correlation": False,
        }
        headers = {"authorization": environment.site_admin_user_token}
        response = client.put("/attributes/0", json=request_body, headers=headers)
        assert response.status_code == 404
        response = client.put("/attributes/invalid_id", json=request_body, headers=headers)
        assert response.status_code == 404


# --- Test delete attribute by id


class TestDeleteAttribute:
    @staticmethod
    def test_delete_existing_attribute(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)
        setattr(event, "sharing_group_id", sharing_group.id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        attribute = generate_attribute()
        setattr(attribute, "event_id", event_id)
        setattr(attribute, "sharing_group_id", sharing_group.id)

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        attribute_id = attribute.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/attributes/{attribute_id}", headers=headers)

        assert response.status_code == 200

    @staticmethod
    def test_delete_invalid_or_non_existing_attribute() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete("/attributes/0", headers=headers)
        assert response.status_code == 404
        response = client.delete("/attributes/invalid_id", headers=headers)
        assert response.status_code == 404


# --- Test get all attributes


class TestGetAllAttributes:
    @staticmethod
    def test_get_all_attributes(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)
        setattr(event, "sharing_group_id", sharing_group.id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        attribute1 = generate_attribute()
        setattr(attribute1, "event_id", event_id)
        setattr(attribute1, "sharing_group_id", sharing_group.id)

        db.add(attribute1)
        db.commit()
        db.refresh(attribute1)

        attribute2 = generate_attribute()
        setattr(attribute2, "event_id", event_id)
        setattr(attribute2, "sharing_group_id", sharing_group.id)

        db.add(attribute2)
        db.commit()
        db.refresh(attribute2)

        headers = {"authorization": environment.site_admin_user_token}
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


class TestDeleteSelectedAttributes:
    @staticmethod
    def test_delete_selected_attributes_from_existing_event(db: Session) -> None:
        request_body = {"id": "1 2 3", "allow_hard_delete": False}
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)
        setattr(event, "sharing_group_id", sharing_group.id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        attribute1 = generate_attribute()
        setattr(attribute1, "event_id", event_id)
        setattr(attribute1, "sharing_group_id", sharing_group.id)

        db.add(attribute1)
        db.commit()
        db.refresh(attribute1)

        attribute1_id = attribute1.id

        attribute2 = generate_attribute()
        setattr(attribute2, "event_id", event_id)
        setattr(attribute2, "sharing_group_id", sharing_group.id)

        db.add(attribute2)
        db.commit()
        db.refresh(attribute2)

        attribute2_id = attribute2.id

        attribute_ids = str(attribute1_id) + " " + str(attribute2_id)

        request_body["id"] = attribute_ids

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/attributes/deleteSelected/{event_id}", json=request_body, headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        counter_of_selected_attributes = len(attribute_ids)
        if counter_of_selected_attributes == 1:
            assert response_json["message"] == "1 attribute deleted."
        else:
            assert response_json["message"] == "2 attributes deleted."
        assert response_json["url"] == f"/attributes/deleteSelected/{event_id}"


class TestAttributesRestSearch:
    @staticmethod
    def test_valid_search_attribute_data(db: Session) -> None:
        request_body = {"returnFormat": "json", "limit": 100}
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)
        setattr(event, "sharing_group_id", sharing_group.id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        attribute = generate_attribute()
        setattr(attribute, "event_id", event_id)
        setattr(attribute, "sharing_group_id", sharing_group.id)

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/attributes/restSearch", json=request_body, headers=headers)
        assert response.status_code == 200
        response_json = response.json()
        assert "response" in response_json
        assert isinstance(response_json["response"], list)
        response_json_attribute = response_json["response"][0]
        assert "Attribute" in response_json_attribute

    @staticmethod
    def test_invalid_search_attribute_data() -> None:
        request_body = {"returnFormat": "invalid format"}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/attributes/restSearch", json=request_body, headers=headers)
        assert response.status_code == 404


# --- Test attribute statistics


class TestAttributeStatistics:
    @staticmethod
    def test_valid_parameters_attribute_statistics() -> None:
        request_body = {"context": "category", "percentage": "1"}
        context = request_body["context"]
        percentage = request_body["percentage"]
        headers = {"authorization": environment.site_admin_user_token}
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

    @staticmethod
    def test_invalid_parameters_attribute_statistics() -> None:
        request_body = {"context": "invalid context", "percentage": 2}
        context = request_body["context"]
        percentage = request_body["percentage"]
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/attributes/attributeStatistics/{context}/{percentage}", headers=headers)
        assert response.status_code == 405


# --- Test attribute describe types


class TestAttributeDescribeTypes:
    @staticmethod
    def test_attribute_describe_types() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/attributes/describeTypes", headers=headers)
        assert response.status_code == 200


# --- Test restore attribute


class TestRestoreAttribute:
    @staticmethod
    def test_restore_existing_attribute(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)
        setattr(event, "sharing_group_id", sharing_group.id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        attribute = generate_attribute()
        attribute.event_id = event_id
        setattr(attribute, "event_id", event_id)
        setattr(attribute, "sharing_group_id", sharing_group.id)

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        attribute_id = attribute.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/attributes/restore/{attribute_id}", headers=headers)
        assert response.status_code == 200

    @staticmethod
    def test_restore_invalid_attribute() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/attributes/restore/0", headers=headers)
        assert response.status_code == 404
        response = client.post("/attributes/restore/invalid_id", headers=headers)
        assert response.status_code == 404


# --- Test adding a tag


class TestAddTagToAttribute:
    @staticmethod
    def test_add_existing_tag_to_attribute(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)
        setattr(event, "sharing_group_id", sharing_group.id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        attribute = generate_attribute()
        setattr(attribute, "event_id", event_id)
        setattr(attribute, "sharing_group_id", sharing_group.id)

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        attribute_id = attribute.id

        tag = generate_tag()
        setattr(tag, "user_id", 1)
        setattr(tag, "org_id", 1)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        tag_id = tag.id

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            f"/attributes/addTag/{attribute_id}/{tag_id}/local:1",
            headers=headers,
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["saved"]
        assert response_json["success"] == "Tag added"
        assert response_json["check_publish"]

    @staticmethod
    def test_add_invalid_or_non_existing_tag_to_attribute(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)
        setattr(event, "sharing_group_id", sharing_group.id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        attribute = generate_attribute()
        setattr(attribute, "event_id", event_id)
        setattr(attribute, "sharing_group_id", sharing_group.id)

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        attribute_id = attribute.id

        headers = {"authorization": environment.site_admin_user_token}
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


class TestRemoveTagFromAttribute:
    @staticmethod
    def test_remove_existing_tag_from_attribute(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        event = generate_event()
        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)
        setattr(event, "sharing_group_id", sharing_group.id)

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        attribute = generate_attribute()
        setattr(attribute, "event_id", event_id)
        setattr(attribute, "sharing_group_id", sharing_group.id)

        db.add(attribute)
        db.commit()
        db.refresh(attribute)

        attribute_id = attribute.id

        tag = generate_tag()
        setattr(tag, "user_id", 1)
        setattr(tag, "org_id", 1)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        tag_id = tag.id

        attribute_tag = AttributeTag(attribute_id=attribute_id, event_id=event_id, tag_id=tag_id, local=False)

        db.add(attribute_tag)
        db.commit()
        db.refresh(attribute_tag)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/attributes/removeTag/{attribute_id}/{tag_id}", headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["saved"]
        assert response_json["success"] == "Tag removed"
