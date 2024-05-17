from datetime import datetime
from time import time_ns
from typing import Any
from uuid import uuid4

import pytest
import sqlalchemy as sa
from fastapi import status
from icecream import ic
from sqlalchemy.orm import Session

from mmisp.db.models.sharing_group import SharingGroup, SharingGroupOrg, SharingGroupServer
from mmisp.util.uuid import uuid


def delete_sharing_group_server(db, sharing_group_id):
    stmt = sa.sql.text("DELETE FROM sharing_group_servers WHERE sharing_group_id=:id")
    db.execute(stmt, {"id": sharing_group_id})
    db.commit()


def delete_sharing_group_orgs(db, sharing_group_id):
    stmt = sa.sql.text("DELETE FROM sharing_group_orgs WHERE sharing_group_id=:id")
    db.execute(stmt, {"id": sharing_group_id})
    db.commit()
    db.commit()


def delete_sharing_group(db, sharing_group_id):
    stmt = sa.sql.text("DELETE FROM sharing_groups WHERE id=:id")
    db.execute(stmt, {"id": sharing_group_id})
    db.commit()


@pytest.fixture(autouse=True)
def check_counts_stay_constant(db):
    count_sharing_groups = db.execute("SELECT COUNT(*) FROM sharing_groups").first()[0]
    count_sharing_groups_orgs = db.execute("SELECT COUNT(*) FROM sharing_group_orgs").first()[0]
    count_sharing_groups_servers = db.execute("SELECT COUNT(*) FROM sharing_group_servers").first()[0]
    yield
    ncount_sharing_groups = db.execute("SELECT COUNT(*) FROM sharing_groups").first()[0]
    ncount_sharing_groups_orgs = db.execute("SELECT COUNT(*) FROM sharing_group_orgs").first()[0]
    ncount_sharing_groups_servers = db.execute("SELECT COUNT(*) FROM sharing_group_servers").first()[0]

    sharing_groups = db.execute("SELECT * FROM sharing_groups").all()
    sharing_groups_orgs = db.execute("SELECT * FROM sharing_group_orgs").all()
    sharing_groups_servers = db.execute("SELECT * FROM sharing_group_servers").all()

    ic(sharing_groups)
    ic(sharing_groups_orgs)
    ic(sharing_groups_servers)

    assert count_sharing_groups == ncount_sharing_groups
    assert count_sharing_groups_orgs == ncount_sharing_groups_orgs
    assert count_sharing_groups_servers == ncount_sharing_groups_servers


def test_create_valid_sharing_group(db: Session, site_admin_user_token, instance_owner_org, client) -> None:
    body = {"name": f"Test Sharing Group {uuid()}{time_ns()}", "description": "description", "releasability": "yes"}

    response = client.post("/sharing_groups", headers={"authorization": site_admin_user_token}, json=body)

    assert response.status_code == status.HTTP_201_CREATED
    json: dict = response.json()
    assert json["org_id"] == str(instance_owner_org.id)
    assert json["organisation_uuid"] == instance_owner_org.uuid

    db_sharing_group_org: SharingGroupOrg = (
        db.query(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == json["id"]).first()
    )
    db_sharing_group_server: SharingGroupServer = (
        db.query(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == json["id"]).first()
    )
    ic(db_sharing_group_org.asdict())
    assert db_sharing_group_org.org_id == instance_owner_org.id
    assert db_sharing_group_server

    delete_sharing_group(db, json["id"])
    delete_sharing_group_orgs(db, json["id"])
    delete_sharing_group_server(db, json["id"])


def test_create_valid_sharing_group_with_org_id_overwrite(
    db: Session, instance_two_owner_org, site_admin_user_token, client
) -> None:
    body = {
        "name": f"test_create_valid_sharing_group_with_org_id_overwrite-{uuid()}",
        "description": "description",
        "releasability": "yes",
        "organisation_uuid": instance_two_owner_org.uuid,
    }

    response = client.post("/sharing_groups", headers={"authorization": site_admin_user_token}, json=body)

    assert response.status_code == status.HTTP_201_CREATED
    json: dict = response.json()
    assert json["org_id"] == str(instance_two_owner_org.id)
    assert json["organisation_uuid"] == instance_two_owner_org.uuid

    db_sharing_group_org: SharingGroupOrg | Any = (
        db.query(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == json["id"]).first()
    )
    db_sharing_group_server: SharingGroupServer | None = (
        db.query(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == json["id"]).first()
    )

    assert db_sharing_group_org.org_id == instance_two_owner_org.id
    assert db_sharing_group_server
    delete_sharing_group(db, json["id"])
    delete_sharing_group_orgs(db, json["id"])
    delete_sharing_group_server(db, json["id"])


def test_create_sharing_group_with_org_id_overwrite_but_not_enough_permissions(
    db, instance_two_owner_org, instance_owner_org_admin_user_token, instance_owner_org, client
) -> None:
    body = {
        "name": f"test_create_sharing_group_with_org_id_overwrite_but_not_enough_permissions-{uuid()}",
        "description": "description",
        "releasability": "yes",
        "organisation_uuid": instance_two_owner_org.uuid,
    }

    response = client.post("/sharing_groups", headers={"authorization": instance_owner_org_admin_user_token}, json=body)

    assert response.status_code == status.HTTP_201_CREATED
    json: dict = response.json()
    assert json["org_id"] == str(instance_owner_org.id)
    assert json["organisation_uuid"] == instance_owner_org.uuid

    delete_sharing_group(db, json["id"])
    delete_sharing_group_orgs(db, json["id"])
    delete_sharing_group_server(db, json["id"])


def test_get_own_created_sharing_group(
    db: Session, sharing_group, instance_owner_org, instance_owner_org_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == str(sharing_group.id)


def test_get_sharing_group_with_access_through_sharing_group_org(
    db: Session, sharing_group, sharing_group_org_two, instance_org_two_admin_user_token, client
) -> None:
    assert sharing_group_org_two

    response = client.get(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == str(sharing_group.id)


def test_get_sharing_group_with_access_through_sharing_group_server(
    db: Session, sharing_group, sharing_group_server_all_orgs, instance_org_two_admin_user_token, client
) -> None:
    assert sharing_group
    assert sharing_group_server_all_orgs
    sharing_group_server_all_orgs.server_id = 0
    db.commit()
    response = client.get(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == str(sharing_group.id)


def test_get_sharing_group_with_access_through_site_admin(
    db: Session, sharing_group, site_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == str(sharing_group.id)


def test_get_sharing_group_with_no_access(
    db: Session, sharing_group, sharing_group_server, instance_org_two, instance_org_two_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )
    ic(instance_org_two.asdict())
    ic(response.json())

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_own_sharing_group(db: Session, sharing_group, instance_owner_org_admin_user_token, client) -> None:
    new_description = f"this is a new description + {datetime.utcnow()}"

    response = client.put(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": instance_owner_org_admin_user_token},
        json={"description": new_description},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == str(sharing_group.id)
    assert json["uuid"] == sharing_group.uuid
    assert json["name"] == sharing_group.name
    assert json["description"] == new_description


def test_update_sharing_group_with_access_through_site_admin(
    db: Session, sharing_group, site_admin_user_token, client
) -> None:
    new_description = f"this is a new description + {datetime.utcnow()}"

    response = client.put(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
        json={"description": new_description, "organisation_uuid": str(uuid4())},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == str(sharing_group.id)
    assert json["uuid"] == sharing_group.uuid
    assert json["name"] == sharing_group.name
    assert json["description"] == new_description


def test_update_sharing_group_no_access_although_sharing_group_org_exists(
    db: Session, sharing_group, sharing_group_org, instance_org_two_admin_user_token, client
) -> None:
    assert sharing_group_org
    new_description = f"this is a new description + {datetime.utcnow()}"

    response = client.put(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
        json={"description": new_description},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_own_sharing_group(
    db: Session, sharing_group, sharing_group_org, sharing_group_server, instance_owner_org_admin_user_token, client
) -> None:
    sharing_group_id = sharing_group.id
    sharing_group_org_id = sharing_group_org.id
    sharing_group_server_id = sharing_group_server.id

    response = client.delete(
        f"/sharing_groups/{sharing_group_id}",
        headers={"authorization": instance_owner_org_admin_user_token},
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
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert second_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_sharing_group_with_access_through_site_admin(
    db: Session, sharing_group, instance_org_two, site_admin_user_token, client
) -> None:
    response = client.delete(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == str(sharing_group.id)

    second_response = client.delete(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
    )

    assert second_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_sharing_group_no_access_although_sharing_group_org_exists(
    db: Session,
    sharing_group,
    sharing_group_org_two,
    instance_owner_org,
    instance_org_two,
    instance_org_two_admin_user_token,
    client,
) -> None:
    response = client.delete(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_own_sharing_group(db: Session, sharing_group, instance_owner_org_admin_user_token, client) -> None:
    response = client.get(
        "/sharing_groups",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    ic(json)
    sharing_group_items = [item for item in json["response"] if item["SharingGroup"]["id"] == str(sharing_group.id)]
    sharing_group_item = sharing_group_items[0]

    assert sharing_group_item
    assert sharing_group_item["editable"]
    assert sharing_group_item["deletable"]


def test_list_own_sharing_group_site_admin(
    db: Session, sharing_group, instance_owner_org, site_admin_user_token, client
) -> None:
    response = client.get(
        "/sharing_groups",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    sharing_group_item = next(
        (item for item in json["response"] if item["SharingGroup"]["id"] == str(sharing_group.id)), None
    )

    assert sharing_group_item
    assert sharing_group_item["editable"]
    assert sharing_group_item["deletable"]


def test_list_sharing_group_with_access_through_sharing_group_org(
    db: Session, sharing_group_org_two, instance_org_two_admin_user_token, site_admin_user_token, client
) -> None:
    response = client.get(
        "/sharing_groups",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    ic(json)

    response = client.get(
        "/sharing_groups",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    ic(json)
    sharing_group_items = [
        item for item in json["response"] if item["SharingGroup"]["id"] == str(sharing_group_org_two.sharing_group_id)
    ]
    ic(sharing_group_items, sharing_group_org_two.id)
    sharing_group_item = sharing_group_items[0]

    assert sharing_group_item
    assert sharing_group_item["SharingGroupOrg"][0]["Organisation"]
    assert not sharing_group_item["editable"]
    assert not sharing_group_item["deletable"]


def test_list_sharing_group_with_access_through_sharing_group_server(
    db: Session,
    sharing_group,
    sharing_group_server_all_orgs,
    instance_org_two_admin_user_token,
    site_admin_user_token,
    client,
) -> None:
    assert sharing_group_server_all_orgs

    sharing_group_server_all_orgs.server_id = 0
    db.commit()

    response = client.get(
        "/sharing_groups",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    ic(json)
    response = client.get(
        "/sharing_groups",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    ic(json)
    ic(sharing_group.asdict())
    sharing_group_items = [item for item in json["response"] if item["SharingGroup"]["id"] == str(sharing_group.id)]
    sharing_group_item = sharing_group_items[0]

    assert sharing_group_item
    assert sharing_group_item["SharingGroupServer"][0]["Server"]["id"] == "0"
    assert not sharing_group_item["editable"]
    assert not sharing_group_item["deletable"]


def test_list_sharing_group_with_no_access(
    db: Session, sharing_group, sharing_group_server, instance_org_two, instance_org_two_admin_user_token, client
) -> None:
    response = client.get(
        "/sharing_groups",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    sharing_group_item = next(
        (item for item in json["response"] if item["SharingGroup"]["id"] == str(sharing_group.id)), None
    )

    assert not sharing_group_item


def test_get_own_created_sharing_group_info(
    db: Session, sharing_group, instance_owner_org_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/{sharing_group.id}/info",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    assert json["SharingGroup"]["id"] == str(sharing_group.id)
    assert json["SharingGroup"]["org_count"] == 0


def test_get_sharing_group_info_with_access_through_sharing_group_org(
    sharing_group, sharing_group_org_two, instance_org_two_admin_user_token, client
) -> None:
    assert sharing_group_org_two
    response = client.get(
        f"/sharing_groups/{sharing_group.id}/info",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    assert json["SharingGroup"]["id"] == str(sharing_group.id)
    assert json["SharingGroup"]["org_count"] == 1


def test_get_sharing_group_info_with_access_through_sharing_group_server(
    db, sharing_group, sharing_group_server_all_orgs, instance_org_two_admin_user_token, client
) -> None:
    sharing_group_server_all_orgs.server_id = 0
    db.commit()

    assert sharing_group_server_all_orgs
    response = client.get(
        f"/sharing_groups/{sharing_group.id}/info",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    assert json["SharingGroup"]["id"] == str(sharing_group.id)
    assert json["SharingGroup"]["org_count"] == 0


def test_get_sharing_group_info_with_access_through_site_admin(
    db: Session, site_admin_user_token, sharing_group, client
) -> None:
    response = client.get(
        f"/sharing_groups/{sharing_group.id}/info",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    assert json["SharingGroup"]["id"] == str(sharing_group.id)
    assert json["SharingGroup"]["org_count"] == 0


def test_get_sharing_group_info_with_no_access(
    db: Session, sharing_group_server, sharing_group, instance_org_two, instance_org_two_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/{sharing_group.id}/info",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_org_to_own_sharing_group(
    db: Session, sharing_group, instance_owner_org, instance_owner_org_admin_user_token, client
) -> None:
    response = client.patch(
        f"/sharing_groups/{sharing_group.id}/organisations",
        headers={"authorization": instance_owner_org_admin_user_token},
        json={"organisationId": "999"},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    ic(json)
    assert json["org_id"] == str(999)
    delete_sharing_group_orgs(db, sharing_group.id)


def test_patch_org_to_own_sharing_group(
    db: Session, sharing_group_org, instance_owner_org, instance_owner_org_admin_user_token, sharing_group, client
) -> None:
    response = client.patch(
        f"/sharing_groups/{sharing_group.id}/organisations",
        headers={"authorization": instance_owner_org_admin_user_token},
        json={"organisationId": "999", "extend": True},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    ic(json, sharing_group_org.asdict())
    assert json["org_id"] == str(999)
    assert json["extend"]

    delete_sharing_group_orgs(db, sharing_group.id)


def test_add_org_to_sharing_group_using_site_admin(
    db: Session, instance_org_two, site_admin_user_token, sharing_group, client
) -> None:
    response = client.patch(
        f"/sharing_groups/{sharing_group.id}/organisations",
        headers={"authorization": site_admin_user_token},
        json={"organisationId": "999"},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["sharing_group_id"] == str(sharing_group.id)

    delete_sharing_group_orgs(db, sharing_group.id)


def test_add_org_to_sharing_group_with_no_access(
    db: Session, sharing_group2, sharing_group_org, instance_owner_org, instance_owner_org_admin_user_token, client
) -> None:
    response = client.patch(
        f"/sharing_groups/{sharing_group2.id}/organisations",
        headers={"authorization": instance_owner_org_admin_user_token},
        json={"organisationId": "999"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_org_from_own_sharing_group(
    db: Session, instance_owner_org, sharing_group, sharing_group_org, instance_owner_org_admin_user_token, client
) -> None:
    sharing_group_org_id = sharing_group_org.id

    response = client.delete(
        f"/sharing_groups/{sharing_group.id}/organisations/{instance_owner_org.id}",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK

    db.invalidate()

    db_sharing_group_org = db.get(SharingGroupOrg, sharing_group_org_id)

    assert not db_sharing_group_org


def test_add_server_to_own_sharing_group(db, sharing_group, instance_owner_org_admin_user_token, client) -> None:
    response = client.patch(
        f"/sharing_groups/{sharing_group.id}/servers",
        headers={"authorization": instance_owner_org_admin_user_token},
        json={"serverId": "999"},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["sharing_group_id"] == str(sharing_group.id)

    delete_sharing_group_server(db, sharing_group.id)


def test_patch_server_to_own_sharing_group(
    db, sharing_group_server, sharing_group, instance_owner_org_admin_user_token, client
) -> None:
    response = client.patch(
        f"/sharing_groups/{sharing_group.id}/servers",
        headers={"authorization": instance_owner_org_admin_user_token},
        json={"serverId": "999", "all_orgs": True},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    ic(json)
    assert json["server_id"] == str(999)
    assert json["all_orgs"]

    delete_sharing_group_server(db, sharing_group.id)


def test_add_server_to_sharing_group_using_site_admin(
    db: Session, sharing_group, site_admin_user_token, client
) -> None:
    response = client.patch(
        f"/sharing_groups/{sharing_group.id}/servers",
        headers={"authorization": site_admin_user_token},
        json={"serverId": "999"},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["sharing_group_id"] == str(sharing_group.id)
    delete_sharing_group_server(db, sharing_group.id)


def test_add_server_to_sharing_group_with_no_access(
    db: Session, sharing_group, sharing_group_org, instance_owner_org, instance_org_two_admin_user_token, client
) -> None:
    response = client.patch(
        f"/sharing_groups/{sharing_group.id}/servers",
        headers={"authorization": instance_org_two_admin_user_token},
        json={"serverId": "999"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_server_from_own_sharing_group(
    db: Session, sharing_group_server, sharing_group, instance_owner_org_admin_user_token, client
) -> None:
    print("----------------- BEGIN TESTCASE ------------------")
    sharing_group_server_id = sharing_group_server.id
    ic(sharing_group_server.asdict())
    url = f"/sharing_groups/{sharing_group.id}/servers/{sharing_group_server.server_id}"
    ic(url)
    response = client.delete(
        url,
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK

    db.invalidate()

    db_sharing_group_server = db.get(SharingGroupServer, sharing_group_server_id)

    assert not db_sharing_group_server


def test_create_valid_sharing_group_legacy(db, instance_owner_org, site_admin_user_token, client) -> None:
    body = {"name": f"Test Sharing Group {uuid()}{time_ns()}", "description": "description", "releasability": "yes"}

    response = client.post("/sharing_groups/add", headers={"authorization": site_admin_user_token}, json=body)

    assert response.status_code == status.HTTP_201_CREATED
    json: dict = response.json()
    assert json["SharingGroup"]["org_id"] == str(instance_owner_org.id)
    assert json["SharingGroup"]["organisation_uuid"] == instance_owner_org.uuid
    assert json["SharingGroupOrg"][0]["org_id"] == str(instance_owner_org.id)
    assert json["SharingGroupServer"][0]["server_id"] == "0"

    ic(json)

    db_sharing_group_org: SharingGroupOrg | Any = (
        db.query(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == json["SharingGroup"]["id"]).first()
    )
    db.delete(db_sharing_group_org)
    db.commit()
    delete_sharing_group(db, json["SharingGroup"]["id"])
    delete_sharing_group_server(db, json["SharingGroup"]["id"])


def test_create_valid_sharing_group_legacy_with_org_id_overwrite(
    db, site_admin_user_token, instance_two_owner_org, client
) -> None:
    body = {
        "name": f"Test Sharing Group {uuid()}{time_ns()}",
        "description": "description",
        "releasability": "yes",
        "organisation_uuid": instance_two_owner_org.uuid,
    }

    response = client.post("/sharing_groups/add", headers={"authorization": site_admin_user_token}, json=body)

    assert response.status_code == status.HTTP_201_CREATED
    json: dict = response.json()
    assert json["SharingGroup"]["org_id"] == str(instance_two_owner_org.id)
    assert json["SharingGroup"]["organisation_uuid"] == instance_two_owner_org.uuid
    assert json["SharingGroupOrg"][0]["org_id"] == str(instance_two_owner_org.id)
    assert json["SharingGroupServer"][0]["server_id"] == "0"

    delete_sharing_group(db, json["SharingGroup"]["id"])
    delete_sharing_group_orgs(db, json["SharingGroup"]["id"])
    delete_sharing_group_server(db, json["SharingGroup"]["id"])


def test_create_sharing_group_legacy_with_org_id_overwrite_but_not_enough_permissions(
    db, instance_two_owner_org, instance_owner_org, instance_owner_org_admin_user_token, client
) -> None:
    body = {
        "name": f"Test Sharing Group {uuid()}{time_ns()}",
        "description": "description",
        "releasability": "yes",
        "organisation_uuid": instance_two_owner_org.uuid,
    }

    response = client.post(
        "/sharing_groups/add", headers={"authorization": instance_owner_org_admin_user_token}, json=body
    )

    assert response.status_code == status.HTTP_201_CREATED
    json: dict = response.json()
    assert json["SharingGroup"]["org_id"] == str(instance_owner_org.id)
    assert json["SharingGroup"]["organisation_uuid"] == instance_owner_org.uuid
    assert json["SharingGroupOrg"][0]["org_id"] == str(instance_owner_org.id)
    assert json["SharingGroupServer"][0]["server_id"] == "0"

    delete_sharing_group(db, json["SharingGroup"]["id"])
    delete_sharing_group_orgs(db, json["SharingGroup"]["id"])
    delete_sharing_group_server(db, json["SharingGroup"]["id"])


def test_get_own_created_sharing_group_legacy(
    db: Session, sharing_group, instance_owner_org_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/view/{sharing_group.id}",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["SharingGroup"]["id"] == str(sharing_group.id)


def test_get_sharing_group_legacy_with_access_through_sharing_group_org(
    db: Session, sharing_group, sharing_group_org_two, instance_org_two_admin_user_token, client
) -> None:
    assert sharing_group_org_two

    response = client.get(
        f"/sharing_groups/view/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["SharingGroup"]["id"] == str(sharing_group.id)


def test_get_sharing_group_legacy_with_access_through_sharing_group_server(
    db: Session, sharing_group, sharing_group_server_all_orgs, instance_org_two_admin_user_token, client
) -> None:
    assert sharing_group_server_all_orgs
    sharing_group_server_all_orgs.server_id = 0
    db.commit()

    response = client.get(
        f"/sharing_groups/view/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["SharingGroup"]["id"] == str(sharing_group.id)


def test_get_sharing_group_legacy_with_access_through_site_admin(
    db: Session, sharing_group, instance_org_two, site_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/view/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["SharingGroup"]["id"] == str(sharing_group.id)


def test_get_sharing_group_legacy_with_no_access(
    db: Session, sharing_group, sharing_group_server, instance_org_two_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/view/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_own_sharing_group_legacy(
    db: Session, sharing_group, instance_owner_org_admin_user_token, client
) -> None:
    new_description = f"this is a new description + {datetime.utcnow()}"

    response = client.post(
        f"/sharing_groups/edit/{sharing_group.id}",
        headers={"authorization": instance_owner_org_admin_user_token},
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


def test_update_sharing_group_legacy_with_access_through_site_admin(
    db: Session, sharing_group, instance_org_two, site_admin_user_token, client
) -> None:
    new_description = f"this is a new description + {datetime.utcnow()}"

    response = client.post(
        f"/sharing_groups/edit/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
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


def test_update_sharing_group_legacy_no_access_although_sharing_group_org_exists(
    db: Session, sharing_group, sharing_group_org, instance_owner_org, instance_org_two_admin_user_token, client
) -> None:
    new_description = f"this is a new description + {datetime.utcnow()}"

    response = client.post(
        f"/sharing_groups/edit/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
        json={
            "name": sharing_group.name,
            "releasability": sharing_group.releasability,
            "description": new_description,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_own_sharing_group_legacy(
    db: Session,
    instance_owner_org,
    sharing_group,
    sharing_group_org,
    sharing_group_server,
    instance_owner_org_admin_user_token,
    client,
) -> None:
    sharing_group_id = sharing_group.id
    sharing_group_org_id = sharing_group_org.id
    sharing_group_server_id = sharing_group_server.id

    response = client.delete(
        f"/sharing_groups/delete/{sharing_group_id}",
        headers={"authorization": instance_owner_org_admin_user_token},
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
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert second_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_sharing_group_legacy_with_access_through_site_admin(
    db: Session, sharing_group, instance_org_two, site_admin_user_token, client
) -> None:
    response = client.delete(
        f"/sharing_groups/delete/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == str(sharing_group.id)
    assert json["saved"]
    assert json["success"]

    second_response = client.delete(
        f"/sharing_groups/delete/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
    )

    assert second_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_sharing_group_legacy_no_access_although_sharing_group_org_exists(
    db: Session, sharing_group, sharing_group_org, instance_owner_org, instance_org_two_admin_user_token, client
) -> None:
    response = client.delete(
        f"/sharing_groups/delete/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_org_to_own_sharing_group_legacy(
    db: Session, sharing_group, instance_owner_org_admin_user_token, client
) -> None:
    response = client.post(
        f"/sharing_groups/addOrg/{sharing_group.id}/999",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["saved"]
    assert json["success"]

    delete_sharing_group_orgs(db, sharing_group.id)


def test_patch_org_to_own_sharing_group_legacy(
    db: Session, sharing_group, sharing_group_org, instance_owner_org_admin_user_token, client
) -> None:
    sharing_group_org.extend = True
    db.commit()
    sharing_group_org_id = sharing_group_org.id

    response = client.post(
        f"/sharing_groups/addOrg/{sharing_group.id}/999",
        headers={"authorization": instance_owner_org_admin_user_token},
        json={"extend": True},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["saved"]
    assert json["success"]

    db.invalidate()

    db_sharing_group_org: SharingGroupOrg = db.get(SharingGroupOrg, sharing_group_org_id)

    ic(db_sharing_group_org.asdict())
    assert db_sharing_group_org.extend

    delete_sharing_group_server(db, sharing_group.id)
    delete_sharing_group_orgs(db, sharing_group.id)


def test_add_org_to_sharing_group_legacy_using_site_admin(
    db: Session, sharing_group, site_admin_user_token, client
) -> None:
    response = client.post(
        f"/sharing_groups/addOrg/{sharing_group.id}/999",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["saved"]
    assert json["success"]

    delete_sharing_group_orgs(db, sharing_group.id)


def test_add_org_to_sharing_group_legacy_with_no_access(
    db: Session,
    instance_org_two,
    sharing_group_org,
    instance_org_two_admin_user_token,
    sharing_group,
    instance_owner_org,
    client,
) -> None:
    response = client.post(
        f"/sharing_groups/addOrg/{sharing_group.id}/999",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_org_from_own_sharing_group_legacy(
    db: Session, sharing_group, sharing_group_org, instance_owner_org, instance_owner_org_admin_user_token, client
) -> None:
    sharing_group_org_id = sharing_group_org.id

    response = client.post(
        f"/sharing_groups/removeOrg/{sharing_group.id}/{instance_owner_org.id}",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["saved"]
    assert json["success"]

    db.invalidate()

    db_sharing_group_org = db.get(SharingGroupOrg, sharing_group_org_id)

    assert not db_sharing_group_org


def test_add_server_to_own_sharing_group_legacy(
    db: Session, sharing_group, instance_owner_org_admin_user_token, client
) -> None:
    response = client.post(
        f"/sharing_groups/addServer/{sharing_group.id}/999",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["saved"]
    assert json["success"]

    delete_sharing_group_server(db, sharing_group.id)


def test_patch_server_to_own_sharing_group_legacy(
    db: Session, sharing_group, sharing_group_server_all_orgs, instance_owner_org_admin_user_token, client
) -> None:
    sharing_group_server_id = sharing_group_server_all_orgs.id

    response = client.post(
        f"/sharing_groups/addServer/{sharing_group.id}/999",
        headers={"authorization": instance_owner_org_admin_user_token},
        json={"all_orgs": True},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["saved"]
    assert json["success"]

    db.invalidate()

    db_sharing_group_server: SharingGroupServer = db.get(SharingGroupServer, sharing_group_server_id)

    assert db_sharing_group_server.all_orgs
    delete_sharing_group_server(db, sharing_group.id)


def test_add_server_to_sharing_group_legeacy_using_site_admin(
    db: Session, sharing_group, site_admin_user_token, client
) -> None:
    response = client.post(
        f"/sharing_groups/addServer/{sharing_group.id}/999",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["saved"]
    assert json["success"]

    delete_sharing_group_server(db, sharing_group.id)


def test_add_server_to_sharing_group_legacy_with_no_access(
    db: Session, sharing_group, instance_owner_org, sharing_group_org, instance_org_two_admin_user_token, client
) -> None:
    response = client.post(
        f"/sharing_groups/addServer/{sharing_group.id}/999",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_server_from_own_sharing_group_legacy(
    db: Session, sharing_group, sharing_group_server, instance_owner_org, instance_owner_org_admin_user_token, client
) -> None:
    sharing_group_server_id = sharing_group_server.id

    response = client.post(
        f"/sharing_groups/removeServer/{sharing_group.id}/{sharing_group_server.server_id}",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK

    db.invalidate()

    db_sharing_group_server = db.get(SharingGroupServer, sharing_group_server_id)

    assert not db_sharing_group_server
