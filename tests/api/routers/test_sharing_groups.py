from datetime import datetime
from time import time_ns
from typing import Any
from uuid import uuid4

from fastapi import status
from sqlalchemy.orm import Session

from mmisp.db.models.sharing_group import SharingGroup, SharingGroupOrg, SharingGroupServer
from mmisp.util.uuid import uuid
from tests.generators.model_generators.sharing_group_generator import generate_sharing_group

from ...environment import client, environment


class TestCreateSharingGroup:
    @staticmethod
    def test_create_valid_sharing_group(db: Session) -> None:
        body = {"name": f"Test Sharing Group {uuid()}{time_ns()}", "description": "description", "releasability": "yes"}

        response = client.post(
            "/sharing_groups", headers={"authorization": environment.site_admin_user_token}, json=body
        )

        assert response.status_code == status.HTTP_201_CREATED
        json: dict = response.json()
        assert json["org_id"] == str(environment.instance_owner_org.id)
        assert json["organisation_uuid"] == environment.instance_owner_org.uuid

        db_sharing_group_org: SharingGroupOrg | Any = (
            db.query(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == json["id"]).first()
        )
        db_sharing_group_server: SharingGroupServer | None = (
            db.query(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == json["id"]).first()
        )

        assert db_sharing_group_org.org_id == environment.instance_owner_org.id
        assert db_sharing_group_server

    @staticmethod
    def test_create_valid_sharing_group_with_org_id_overwrite(db: Session) -> None:
        body = {
            "name": f"Test Sharing Group {uuid()}{time_ns()}",
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

        db_sharing_group_org: SharingGroupOrg | Any = (
            db.query(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == json["id"]).first()
        )
        db_sharing_group_server: SharingGroupServer | None = (
            db.query(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == json["id"]).first()
        )

        assert db_sharing_group_org.org_id == environment.instance_two_owner_org.id
        assert db_sharing_group_server

    @staticmethod
    def test_create_sharing_group_with_org_id_overwrite_but_not_enough_permissions() -> None:
        body = {
            "name": f"Test Sharing Group {uuid()}{time_ns()}",
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
    @staticmethod
    def test_get_own_created_sharing_group(db: Session) -> None:
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

    @staticmethod
    def test_get_sharing_group_with_access_through_sharing_group_org(db: Session) -> None:
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

    @staticmethod
    def test_get_sharing_group_with_access_through_sharing_group_server(db: Session) -> None:
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

    @staticmethod
    def test_get_sharing_group_with_access_through_site_admin(db: Session) -> None:
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

    @staticmethod
    def test_get_sharing_group_with_no_access(db: Session) -> None:
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
            f"/sharing_groups/{sharing_group.id}",
            headers={"authorization": environment.instance_two_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateSharingGroup:
    @staticmethod
    def test_update_own_sharing_group(db: Session) -> None:
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

    @staticmethod
    def test_update_sharing_group_with_access_through_site_admin(db: Session) -> None:
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

    @staticmethod
    def test_update_sharing_group_no_access_although_sharing_group_org_exists(db: Session) -> None:
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
    @staticmethod
    def test_delete_own_sharing_group(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_id = sharing_group.id

        sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=environment.instance_owner_org.id)
        sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=0)

        db.add_all([sharing_group_org, sharing_group_server])
        db.commit()
        db.refresh(sharing_group_org)
        db.refresh(sharing_group_server)

        sharing_group_org_id = sharing_group_org.id
        sharing_group_server_id = sharing_group_server.id

        response = client.delete(
            f"/sharing_groups/{sharing_group_id}",
            headers={"authorization": environment.instance_org_two_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["id"] == str(sharing_group_id)

        db.invalidate()

        db_sharing_group: SharingGroup | None = db.get(SharingGroup, sharing_group_id)
        db_sharing_group_org: SharingGroupOrg | None = db.get(SharingGroupOrg, sharing_group_org_id)
        db_sharing_group_server: SharingGroupServer | None = db.get(SharingGroupServer, sharing_group_server_id)

        assert not db_sharing_group
        assert not db_sharing_group_org
        assert not db_sharing_group_server

        second_response = client.delete(
            f"/sharing_groups/{sharing_group_id}",
            headers={"authorization": environment.instance_org_two_admin_user_token},
        )

        assert second_response.status_code == status.HTTP_404_NOT_FOUND

    @staticmethod
    def test_delete_sharing_group_with_access_through_site_admin(db: Session) -> None:
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

    @staticmethod
    def test_delete_sharing_group_no_access_although_sharing_group_org_exists(db: Session) -> None:
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
    @staticmethod
    def test_list_own_sharing_group(db: Session) -> None:
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

    @staticmethod
    def test_list_sharing_group_with_access_through_sharing_group_org(db: Session) -> None:
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

    @staticmethod
    def test_list_sharing_group_with_access_through_sharing_group_server(db: Session) -> None:
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

    @staticmethod
    def test_list_sharing_group_with_no_access(db: Session) -> None:
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
            headers={"authorization": environment.instance_two_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()

        sharing_group_item = next(
            (item for item in json["response"] if item["SharingGroup"]["id"] == str(sharing_group.id)), None
        )

        assert not sharing_group_item


class TestGetSharingGroupInfo:
    @staticmethod
    def test_get_own_created_sharing_group_info(db: Session) -> None:
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

    @staticmethod
    def test_get_sharing_group_info_with_access_through_sharing_group_org(db: Session) -> None:
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

    @staticmethod
    def test_get_sharing_group_info_with_access_through_sharing_group_server(db: Session) -> None:
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

    @staticmethod
    def test_get_sharing_group_info_with_access_through_site_admin(db: Session) -> None:
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

    @staticmethod
    def test_get_sharing_group_info_with_no_access(db: Session) -> None:
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
            f"/sharing_groups/{sharing_group.id}/info",
            headers={"authorization": environment.instance_two_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAddOrgToSharingGroup:
    @staticmethod
    def test_add_org_to_own_sharing_group(db: Session) -> None:
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

    @staticmethod
    def test_patch_org_to_own_sharing_group(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_org = SharingGroupOrg(
            sharing_group_id=sharing_group.id,
            org_id=999,
            extend=False,
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

    @staticmethod
    def test_add_org_to_sharing_group_using_site_admin(db: Session) -> None:
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

    @staticmethod
    def test_add_org_to_sharing_group_with_no_access(db: Session) -> None:
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
    @staticmethod
    def test_remove_org_from_own_sharing_group(db: Session) -> None:
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

        sharing_group_org_id = sharing_group_org.id

        response = client.delete(
            f"/sharing_groups/{sharing_group.id}/organisations/999",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK

        db.invalidate()

        db_sharing_group_org = db.get(SharingGroupOrg, sharing_group_org_id)

        assert not db_sharing_group_org


class TestAddServerToSharingGroup:
    @staticmethod
    def test_add_server_to_own_sharing_group(db: Session) -> None:
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

    @staticmethod
    def test_patch_server_to_own_sharing_group(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_server = SharingGroupServer(
            sharing_group_id=sharing_group.id,
            server_id=999,
            all_orgs=False,
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

    @staticmethod
    def test_add_server_to_sharing_group_using_site_admin(db: Session) -> None:
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

    @staticmethod
    def test_add_server_to_sharing_group_with_no_access(db: Session) -> None:
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
    @staticmethod
    def test_remove_server_from_own_sharing_group(db: Session) -> None:
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

        sharing_group_server_id = sharing_group_server.id

        response = client.delete(
            f"/sharing_groups/{sharing_group.id}/servers/999",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK

        db.invalidate()

        db_sharing_group_server = db.get(SharingGroupServer, sharing_group_server_id)

        assert not db_sharing_group_server


class TestCreateSharingGroupLegacy:
    @staticmethod
    def test_create_valid_sharing_group_legacy() -> None:
        body = {"name": f"Test Sharing Group {uuid()}{time_ns()}", "description": "description", "releasability": "yes"}

        response = client.post(
            "/sharing_groups/add", headers={"authorization": environment.site_admin_user_token}, json=body
        )

        assert response.status_code == status.HTTP_201_CREATED
        json: dict = response.json()
        assert json["SharingGroup"]["org_id"] == str(environment.instance_owner_org.id)
        assert json["SharingGroup"]["organisation_uuid"] == environment.instance_owner_org.uuid
        assert json["SharingGroupOrg"][0]["org_id"] == str(environment.instance_owner_org.id)
        assert json["SharingGroupServer"][0]["server_id"] == "0"

    @staticmethod
    def test_create_valid_sharing_group_legacy_with_org_id_overwrite() -> None:
        body = {
            "name": f"Test Sharing Group {uuid()}{time_ns()}",
            "description": "description",
            "releasability": "yes",
            "organisation_uuid": environment.instance_two_owner_org.uuid,
        }

        response = client.post(
            "/sharing_groups/add", headers={"authorization": environment.site_admin_user_token}, json=body
        )

        assert response.status_code == status.HTTP_201_CREATED
        json: dict = response.json()
        assert json["SharingGroup"]["org_id"] == str(environment.instance_two_owner_org.id)
        assert json["SharingGroup"]["organisation_uuid"] == environment.instance_two_owner_org.uuid
        assert json["SharingGroupOrg"][0]["org_id"] == str(environment.instance_two_owner_org.id)
        assert json["SharingGroupServer"][0]["server_id"] == "0"

    @staticmethod
    def test_create_sharing_group_legacy_with_org_id_overwrite_but_not_enough_permissions() -> None:
        body = {
            "name": f"Test Sharing Group {uuid()}{time_ns()}",
            "description": "description",
            "releasability": "yes",
            "organisation_uuid": environment.instance_two_owner_org.uuid,
        }

        response = client.post(
            "/sharing_groups/add", headers={"authorization": environment.instance_owner_org_admin_user_token}, json=body
        )

        assert response.status_code == status.HTTP_201_CREATED
        json: dict = response.json()
        assert json["SharingGroup"]["org_id"] == str(environment.instance_owner_org.id)
        assert json["SharingGroup"]["organisation_uuid"] == environment.instance_owner_org.uuid
        assert json["SharingGroupOrg"][0]["org_id"] == str(environment.instance_owner_org.id)
        assert json["SharingGroupServer"][0]["server_id"] == "0"


class TestGetSharingGroupLegacy:
    @staticmethod
    def test_get_own_created_sharing_group_legacy(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.get(
            f"/sharing_groups/view/{sharing_group.id}",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["SharingGroup"]["id"] == str(sharing_group.id)

    @staticmethod
    def test_get_sharing_group_legacy_with_access_through_sharing_group_org(db: Session) -> None:
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
            f"/sharing_groups/view/{sharing_group.id}",
            headers={"authorization": environment.instance_org_two_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["SharingGroup"]["id"] == str(sharing_group.id)

    @staticmethod
    def test_get_sharing_group_legacy_with_access_through_sharing_group_server(db: Session) -> None:
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
            f"/sharing_groups/view/{sharing_group.id}",
            headers={"authorization": environment.instance_org_two_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["SharingGroup"]["id"] == str(sharing_group.id)

    @staticmethod
    def test_get_sharing_group_legacy_with_access_through_site_admin(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.get(
            f"/sharing_groups/view/{sharing_group.id}",
            headers={"authorization": environment.site_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["SharingGroup"]["id"] == str(sharing_group.id)

    @staticmethod
    def test_get_sharing_group_legacy_with_no_access(db: Session) -> None:
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
            f"/sharing_groups/view/{sharing_group.id}",
            headers={"authorization": environment.instance_two_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateSharingGroupLegacy:
    @staticmethod
    def test_update_own_sharing_group_legacy(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        new_description = f"this is a new description + {datetime.utcnow()}"

        response = client.post(
            f"/sharing_groups/edit/{sharing_group.id}",
            headers={"authorization": environment.instance_org_two_admin_user_token},
            json={
                "name": sharing_group.name,
                "releasability": sharing_group.releasability,
                "description": new_description,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["SharingGroup"]["id"] == str(sharing_group.id)
        assert json["SharingGroup"]["uuid"] == sharing_group.uuid
        assert json["SharingGroup"]["name"] == sharing_group.name
        assert json["SharingGroup"]["description"] == new_description

    @staticmethod
    def test_update_sharing_group_legacy_with_access_through_site_admin(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        new_description = f"this is a new description + {datetime.utcnow()}"

        response = client.post(
            f"/sharing_groups/edit/{sharing_group.id}",
            headers={"authorization": environment.site_admin_user_token},
            json={
                "name": sharing_group.name,
                "releasability": sharing_group.releasability,
                "description": new_description,
                "organisation_uuid": str(uuid4()),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["SharingGroup"]["id"] == str(sharing_group.id)
        assert json["SharingGroup"]["uuid"] == sharing_group.uuid
        assert json["SharingGroup"]["name"] == sharing_group.name
        assert json["SharingGroup"]["description"] == new_description

    @staticmethod
    def test_update_sharing_group_legacy_no_access_although_sharing_group_org_exists(db: Session) -> None:
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

        response = client.post(
            f"/sharing_groups/edit/{sharing_group.id}",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
            json={
                "name": sharing_group.name,
                "releasability": sharing_group.releasability,
                "description": new_description,
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteSharingGroupLegacy:
    @staticmethod
    def test_delete_own_sharing_group_legacy(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_id = sharing_group.id

        sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=environment.instance_owner_org.id)
        sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=0)

        db.add_all([sharing_group_org, sharing_group_server])
        db.commit()
        db.refresh(sharing_group_org)
        db.refresh(sharing_group_server)

        sharing_group_org_id = sharing_group_org.id
        sharing_group_server_id = sharing_group_server.id

        response = client.delete(
            f"/sharing_groups/delete/{sharing_group_id}",
            headers={"authorization": environment.instance_org_two_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["id"] == str(sharing_group.id)
        assert json["saved"]
        assert json["success"]

        db.invalidate()

        db_sharing_group: SharingGroup | None = db.get(SharingGroup, sharing_group_id)
        db_sharing_group_org: SharingGroupOrg | None = db.get(SharingGroupOrg, sharing_group_org_id)
        db_sharing_group_server: SharingGroupServer | None = db.get(SharingGroupServer, sharing_group_server_id)

        assert not db_sharing_group
        assert not db_sharing_group_org
        assert not db_sharing_group_server

        second_response = client.delete(
            f"/sharing_groups/delete/{sharing_group_id}",
            headers={"authorization": environment.instance_org_two_admin_user_token},
        )

        assert second_response.status_code == status.HTTP_404_NOT_FOUND

    @staticmethod
    def test_delete_sharing_group_legacy_with_access_through_site_admin(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.delete(
            f"/sharing_groups/delete/{sharing_group.id}",
            headers={"authorization": environment.site_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["id"] == str(sharing_group.id)
        assert json["saved"]
        assert json["success"]

        second_response = client.delete(
            f"/sharing_groups/delete/{sharing_group.id}",
            headers={"authorization": environment.site_admin_user_token},
        )

        assert second_response.status_code == status.HTTP_404_NOT_FOUND

    @staticmethod
    def test_delete_sharing_group_legacy_no_access_although_sharing_group_org_exists(db: Session) -> None:
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
            f"/sharing_groups/delete/{sharing_group.id}",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAddOrgToSharingGroupLegacy:
    @staticmethod
    def test_add_org_to_own_sharing_group_legacy(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.post(
            f"/sharing_groups/addOrg/{sharing_group.id}/999",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["saved"]
        assert json["success"]

    @staticmethod
    def test_patch_org_to_own_sharing_group_legacy(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=999, extend=False)

        db.add(sharing_group_org)
        db.commit()
        db.refresh(sharing_group_org)

        sharing_group_org_id = sharing_group_org.id

        response = client.post(
            f"/sharing_groups/addOrg/{sharing_group.id}/999",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
            json={"extend": True},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["saved"]
        assert json["success"]

        db.invalidate()

        db_sharing_group_org: SharingGroupOrg = db.get(SharingGroupOrg, sharing_group_org_id)

        assert db_sharing_group_org.extend

    @staticmethod
    def test_add_org_to_sharing_group_legacy_using_site_admin(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.post(
            f"/sharing_groups/addOrg/{sharing_group.id}/999",
            headers={"authorization": environment.site_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["saved"]
        assert json["success"]

    @staticmethod
    def test_add_org_to_sharing_group_legacy_with_no_access(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_org = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=environment.instance_owner_org.id)

        db.add(sharing_group_org)
        db.commit()

        response = client.post(
            f"/sharing_groups/addOrg/{sharing_group.id}/999",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRemoveOrgFromSharingGroupLegacy:
    @staticmethod
    def test_remove_org_from_own_sharing_group_legacy(db: Session) -> None:
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

        sharing_group_org_id = sharing_group_org.id

        response = client.post(
            f"/sharing_groups/removeOrg/{sharing_group.id}/999",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["saved"]
        assert json["success"]

        db.invalidate()

        db_sharing_group_org = db.get(SharingGroupOrg, sharing_group_org_id)

        assert not db_sharing_group_org


class TestAddServerToSharingGroupLegacy:
    @staticmethod
    def test_add_server_to_own_sharing_group_legacy(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.post(
            f"/sharing_groups/addServer/{sharing_group.id}/999",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["saved"]
        assert json["success"]

    @staticmethod
    def test_patch_server_to_own_sharing_group_legacy(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_owner_org.uuid
        sharing_group.org_id = environment.instance_owner_org.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        sharing_group_server = SharingGroupServer(sharing_group_id=sharing_group.id, server_id=999, all_orgs=False)

        db.add(sharing_group_server)
        db.commit()
        db.refresh(sharing_group_server)

        sharing_group_server_id = sharing_group_server.id

        response = client.post(
            f"/sharing_groups/addServer/{sharing_group.id}/999",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
            json={"all_orgs": True},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["saved"]
        assert json["success"]

        db.invalidate()

        db_sharing_group_server: SharingGroupServer = db.get(SharingGroupServer, sharing_group_server_id)

        assert db_sharing_group_server.all_orgs

    @staticmethod
    def test_add_server_to_sharing_group_legeacy_using_site_admin(db: Session) -> None:
        sharing_group = generate_sharing_group()
        sharing_group.organisation_uuid = environment.instance_org_two.uuid
        sharing_group.org_id = environment.instance_org_two.id

        db.add(sharing_group)
        db.commit()
        db.refresh(sharing_group)

        response = client.post(
            f"/sharing_groups/addServer/{sharing_group.id}/999",
            headers={"authorization": environment.site_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["saved"]
        assert json["success"]

    @staticmethod
    def test_add_server_to_sharing_group_legacy_with_no_access(db: Session) -> None:
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

        response = client.post(
            f"/sharing_groups/addServer/{sharing_group.id}/999",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRemoveServerFromSharingGroupLegacy:
    @staticmethod
    def test_remove_server_from_own_sharing_group_legacy(db: Session) -> None:
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

        sharing_group_server_id = sharing_group_server.id

        response = client.post(
            f"/sharing_groups/removeServer/{sharing_group.id}/999",
            headers={"authorization": environment.instance_owner_org_admin_user_token},
        )

        assert response.status_code == status.HTTP_200_OK

        db.invalidate()

        db_sharing_group_server = db.get(SharingGroupServer, sharing_group_server_id)

        assert not db_sharing_group_server
