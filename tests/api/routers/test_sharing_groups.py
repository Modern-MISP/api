from datetime import datetime
from uuid import uuid4

from fastapi import status

from mmisp.db.database import get_db
from mmisp.db.models.sharing_group import SharingGroup, SharingGroupOrg, SharingGroupServer
from tests.generators.model_generators.sharing_group_generator import generate_sharing_group

from ...environment import client, environment


class TestCreateSharingGroup:
    def test_create_valid_sharing_group(self: "TestCreateSharingGroup") -> None:
        body = {"name": "Test Sharing Group", "description": "description", "releasability": "yes"}

        response = client.post(
            "/sharing_groups", headers={"authorization": environment.site_admin_user_token}, json=body
        )

        assert response.status_code == status.HTTP_201_CREATED
        json: dict = response.json()
        assert json["org_id"] == str(environment.instance_owner_org.id)
        assert json["organisation_uuid"] == environment.instance_owner_org.uuid

        db = get_db()
        db_sharing_group_org: SharingGroupOrg | None = (
            db.query(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == json["id"]).first()
        )
        db_sharing_group_server: SharingGroupServer | None = (
            db.query(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == json["id"]).first()
        )

        assert db_sharing_group_org.org_id == environment.instance_owner_org.id
        assert db_sharing_group_server

    def test_create_valid_sharing_group_with_org_id_overwrite(self: "TestCreateSharingGroup") -> None:
        body = {
            "name": "Test Sharing Group",
            "description": "description",
            "releasability": "yes",
            "organisation_uuid": environment.instance_two_owner_org.uuid,
        }

        response = client.post(
            "/sharing_groups", headers={"authorization": environment.site_admin_user_token}, json=body
        )

        assert response.status_code == status.HTTP_201_CREATED
        json: dict = response.json()
        assert json["org_id"] == str(environment.instance_two_owner_org.id)
        assert json["organisation_uuid"] == environment.instance_two_owner_org.uuid

        db = get_db()
        db_sharing_group_org: SharingGroupOrg | None = (
            db.query(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == json["id"]).first()
        )
        db_sharing_group_server: SharingGroupServer | None = (
            db.query(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == json["id"]).first()
        )

        assert db_sharing_group_org.org_id == environment.instance_two_owner_org.id
        assert db_sharing_group_server

    def test_create_sharing_group_with_org_id_overwrite_but_not_enough_permissions(
        self: "TestCreateSharingGroup",
    ) -> None:
        body = {
            "name": "Test Sharing Group",
            "description": "description",
            "releasability": "yes",
            "organisation_uuid": environment.instance_two_owner_org.uuid,
        }

        response = client.post(
            "/sharing_groups", headers={"authorization": environment.instance_owner_org_admin_user_token}, json=body
        )

        assert response.status_code == status.HTTP_201_CREATED
        json: dict = response.json()
        assert json["org_id"] == str(environment.instance_owner_org.id)
        assert json["organisation_uuid"] == environment.instance_owner_org.uuid


class TestGetSharingGroup:
    def test_get_own_created_sharing_group(self: "TestGetSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.get(
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["id"] == str(sharing_group.id)

    def test_get_sharing_group_with_access_through_sharing_group_org(self: "TestGetSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=environment.instance_org_two.id)

        db.add(sharing_group_org)
        db.commit()

        response = client.get(
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.instance_org_two_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["id"] == str(sharing_group.id)

    def test_get_sharing_group_with_access_through_sharing_group_server(self: "TestGetSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=0, all_orgs=True)

        db.add(sharing_group_server)
        db.commit()

        response = client.get(
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.instance_org_two_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["id"] == str(sharing_group.id)

    def test_get_sharing_group_with_access_through_site_admin(self: "TestGetSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.get(
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.site_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["id"] == str(sharing_group.id)

    def test_get_sharing_group_with_no_access(self: "TestGetSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.get(
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateSharingGroup:
    def test_update_own_sharing_group(self: "TestUpdateSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        new_description = f"this is a new description + {datetime.utcnow()}"

        response = client.put(
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.instance_org_two_admin_user_token},
            json={"description": new_description},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["id"] == str(sharing_group.id)
        assert json["uuid"] == sharing_group.uuid
        assert json["name"] == sharing_group.name
        assert json["description"] == new_description

    def test_update_sharing_group_with_access_through_site_admin(self: "TestUpdateSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        new_description = f"this is a new description + {datetime.utcnow()}"

        response = client.put(
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.site_admin_user_token},
            json={"description": new_description, "organisation_uuid": str(uuid4())},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["id"] == str(sharing_group.id)
        assert json["uuid"] == sharing_group.uuid
        assert json["name"] == sharing_group.name
        assert json["description"] == new_description

    def test_update_sharing_group_no_access_although_sharing_group_org_exists(self: "TestUpdateSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=environment.instance_owner_org.id)

        db.add(sharing_group_org)
        db.commit()

        new_description = f"this is a new description + {datetime.utcnow()}"

        response = client.put(
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
            json={"description": new_description},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteSharingGroup:
    def test_delete_own_sharing_group(self: "TestDeleteSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=environment.instance_owner_org.id)
        sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=0)

        db.add_all([sharing_group_org, sharing_group_server])
        db.commit()
        db.refresh(sharing_group_org)
        db.refresh(sharing_group_server)

        response = client.delete(
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.instance_org_two_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["id"] == str(sharing_group.id)

        db.close()
        db = get_db()

        db_sharing_group: SharingGroup | None = db.get(SharingGroup, sharing_group.id)
        db_sharing_group_org: SharingGroupOrg | None = db.get(SharingGroupOrg, sharing_group_org.id)
        db_sharing_group_server: SharingGroupServer | None = db.get(SharingGroupServer, sharing_group_server.id)

        assert not db_sharing_group
        assert not db_sharing_group_org
        assert not db_sharing_group_server

        second_response = client.delete(
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.instance_org_two_admin_user_token},
        )

        assert second_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_sharing_group_with_access_through_site_admin(self: "TestDeleteSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.delete(
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.site_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["id"] == str(sharing_group.id)

        second_response = client.delete(
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.site_admin_user_token},
        )

        assert second_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_sharing_group_no_access_although_sharing_group_org_exists(self: "TestDeleteSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=environment.instance_owner_org.id)

        db.add(sharing_group_org)
        db.commit()

        response = client.delete(
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestListSharingGroups:
    def test_list_own_sharing_group(self: "TestListSharingGroups") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.get(
            "/sharing_groups",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()

        sharing_group_item = next(
            (item for item in json["response"] if item["SharingGroup"]["id"] == str(sharing_group.id)), None
        )

        assert sharing_group_item
        assert sharing_group_item["editable"]
        assert sharing_group_item["deletable"]

    def test_list_sharing_group_with_access_through_sharing_group_org(self: "TestListSharingGroups") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=environment.instance_owner_org.id)

        db.add(sharing_group_org)
        db.commit()

        response = client.get(
            "/sharing_groups",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()

        sharing_group_item = next(
            (item for item in json["response"] if item["SharingGroup"]["id"] == str(sharing_group.id)), None
        )

        assert sharing_group_item
        assert sharing_group_item["SharingGroupOrg"][0]["Organisation"]
        assert not sharing_group_item["editable"]
        assert not sharing_group_item["deletable"]

    def test_list_sharing_group_with_access_through_sharing_group_server(self: "TestListSharingGroups") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=0, all_orgs=True)

        db.add(sharing_group_server)
        db.commit()

        response = client.get(
            "/sharing_groups",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()

        sharing_group_item = next(
            (item for item in json["response"] if item["SharingGroup"]["id"] == str(sharing_group.id)), None
        )

        assert sharing_group_item
        assert sharing_group_item["SharingGroupServer"][0]["Server"]["id"] == "0"
        assert not sharing_group_item["editable"]
        assert not sharing_group_item["deletable"]


class TestGetSharingGroupInfo:
    def test_get_own_created_sharing_group_info(self: "TestGetSharingGroupInfo") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.get(
            f"/sharing_groups/{sharing_group.id}/info",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()

        assert json["SharingGroup"]["id"] == str(sharing_group.id)
        assert json["SharingGroup"]["org_count"] == 0

    def test_get_sharing_group_info_with_access_through_sharing_group_org(self: "TestGetSharingGroupInfo") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=environment.instance_org_two.id)

        db.add(sharing_group_org)
        db.commit()

        response = client.get(
            f"/sharing_groups/{sharing_group.id}/info",
            headers={"authorization": environment.instance_org_two_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()

        assert json["SharingGroup"]["id"] == str(sharing_group.id)
        assert json["SharingGroup"]["org_count"] == 1

    def test_get_sharing_group_info_with_access_through_sharing_group_server(self: "TestGetSharingGroupInfo") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=0, all_orgs=True)

        db.add(sharing_group_server)
        db.commit()

        response = client.get(
            f"/sharing_groups/{sharing_group.id}/info",
            headers={"authorization": environment.instance_org_two_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()

        assert json["SharingGroup"]["id"] == str(sharing_group.id)
        assert json["SharingGroup"]["org_count"] == 0

    def test_get_sharing_group_info_with_access_through_site_admin(self: "TestGetSharingGroupInfo") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.get(
            f"/sharing_groups/{sharing_group.id}/info",
            headers={"authorization": environment.site_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()

        assert json["SharingGroup"]["id"] == str(sharing_group.id)
        assert json["SharingGroup"]["org_count"] == 0

    def test_get_sharing_group_info_with_no_access(self: "TestGetSharingGroupInfo") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.get(
            f"/sharing_groups/{sharing_group.id}/info",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAddOrgToSharingGroup:
    def test_add_org_to_own_sharing_group(self: "TestAddOrgToSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.patch(
            f"/sharing_groups/{sharing_group.id}/organisations",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
            json={"organisationId": "999"},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["sharing_group_id"] == str(sharing_group.id)

    def test_patch_org_to_own_sharing_group(self: "TestAddOrgToSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_org = SharingGroupOrg(
            sharing_group_id=sharing_group.id,
            org_id=999,
        )

        db.add(sharing_group_org)
        db.commit()
        db.refresh(sharing_group_org)

        response = client.patch(
            f"/sharing_groups/{sharing_group.id}/organisations",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
            json={"organisationId": "999", "extend": True},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["id"] == str(sharing_group_org.id)
        assert json["extend"]

    def test_add_org_to_sharing_group_using_site_admin(self: "TestAddOrgToSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.patch(
            f"/sharing_groups/{sharing_group.id}/organisations",
            headers={"authorization": environment.site_admin_user_token},
            json={"organisationId": "999"},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["sharing_group_id"] == str(sharing_group.id)

    def test_add_org_to_sharing_group_with_no_access(self: "TestAddOrgToSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=environment.instance_owner_org.id)

        db.add(sharing_group_org)
        db.commit()

        response = client.patch(
            f"/sharing_groups/{sharing_group.id}/organisations",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
            json={"organisationId": "999"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRemoveOrgFromSharingGroup:
    def test_remove_org_from_own_sharing_group(self: "TestRemoveOrgFromSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=999)

        db.add(sharing_group_org)
        db.commit()
        db.refresh(sharing_group_org)

        response = client.delete(
            f"/sharing_groups/{sharing_group.id}/organisations/999",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK

        db.close()
        db = get_db()

        db_sharing_group_org = db.get(SharingGroupOrg, sharing_group_org.id)

        assert not db_sharing_group_org


class TestAddServerToSharingGroup:
    def test_add_server_to_own_sharing_group(self: "TestAddServerToSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.patch(
            f"/sharing_groups/{sharing_group.id}/servers",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
            json={"serverId": "999"},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["sharing_group_id"] == str(sharing_group.id)

    def test_patch_server_to_own_sharing_group(self: "TestAddServerToSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_server = SharingGroupServer(
            sharing_group_id=sharing_group.id,
            server_id=999,
        )

        db.add(sharing_group_server)
        db.commit()
        db.refresh(sharing_group_server)

        response = client.patch(
            f"/sharing_groups/{sharing_group.id}/servers",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
            json={"serverId": "999", "all_orgs": True},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["id"] == str(sharing_group_server.id)
        assert json["all_orgs"]

    def test_add_server_to_sharing_group_using_site_admin(self: "TestAddServerToSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.patch(
            f"/sharing_groups/{sharing_group.id}/servers",
            headers={"authorization": environment.site_admin_user_token},
            json={"serverId": "999"},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["sharing_group_id"] == str(sharing_group.id)

    def test_add_server_to_sharing_group_with_no_access(self: "TestAddServerToSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        # no update access since only read access is shared through SharingGroupOrg
        sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=environment.instance_owner_org.id)

        db.add(sharing_group_org)
        db.commit()

        response = client.patch(
            f"/sharing_groups/{sharing_group.id}/servers",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
            json={"serverId": "999"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRemoveServerFromSharingGroup:
    def test_remove_server_from_own_sharing_group(self: "TestRemoveServerFromSharingGroup") -> None:
        db = get_db()

        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=999)

        db.add(sharing_group_server)
        db.commit()
        db.refresh(sharing_group_server)

        response = client.delete(
            f"/sharing_groups/{sharing_group.id}/servers/999",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK

        db.close()
        db = get_db()

        db_sharing_group_server = db.get(SharingGroupServer, sharing_group_server.id)

        assert not db_sharing_group_server
