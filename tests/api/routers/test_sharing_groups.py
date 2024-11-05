from datetime import datetime
from time import time_ns
from uuid import uuid4

import pytest
import pytest_asyncio
import sqlalchemy as sa
from fastapi import status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.orm import Session

from mmisp.db.models.sharing_group import SharingGroup, SharingGroupOrg, SharingGroupServer
from mmisp.util.uuid import uuid


async def delete_sharing_group_server(db, sharing_group_id):
    stmt = sa.sql.text("DELETE FROM sharing_group_servers WHERE sharing_group_id=:id")
    await db.execute(stmt, {"id": sharing_group_id})
    await db.commit()


async def delete_sharing_group_orgs(db, sharing_group_id):
    stmt = sa.sql.text("DELETE FROM sharing_group_orgs WHERE sharing_group_id=:id")
    await db.execute(stmt, {"id": sharing_group_id})
    await db.commit()
    await db.commit()


async def delete_sharing_group(db, sharing_group_id):
    stmt = sa.sql.text("DELETE FROM sharing_groups WHERE id=:id")
    await db.execute(stmt, {"id": sharing_group_id})
    await db.commit()


@pytest_asyncio.fixture(autouse=True)
async def check_counts_stay_constant(db):
    count_sharing_groups = (await db.execute(sa.sql.text("SELECT COUNT(*) FROM sharing_groups"))).first()[0]
    count_sharing_groups_orgs = (await db.execute(sa.sql.text("SELECT COUNT(*) FROM sharing_group_orgs"))).first()[0]
    count_sharing_groups_servers = (
        await db.execute(sa.sql.text("SELECT COUNT(*) FROM sharing_group_servers"))
    ).first()[0]
    yield
    ncount_sharing_groups = (await db.execute(sa.sql.text("SELECT COUNT(*) FROM sharing_groups"))).first()[0]
    ncount_sharing_groups_orgs = (await db.execute(sa.sql.text("SELECT COUNT(*) FROM sharing_group_orgs"))).first()[0]
    ncount_sharing_groups_servers = (
        await db.execute(sa.sql.text("SELECT COUNT(*) FROM sharing_group_servers"))
    ).first()[0]

    sharing_groups = (await db.execute(sa.sql.text("SELECT * FROM sharing_groups"))).all()
    sharing_groups_orgs = (await db.execute(sa.sql.text("SELECT * FROM sharing_group_orgs"))).all()
    sharing_groups_servers = (await db.execute(sa.sql.text("SELECT * FROM sharing_group_servers"))).all()

    ic(sharing_groups)
    ic(sharing_groups_orgs)
    ic(sharing_groups_servers)

    assert count_sharing_groups == ncount_sharing_groups
    assert count_sharing_groups_orgs == ncount_sharing_groups_orgs
    assert count_sharing_groups_servers == ncount_sharing_groups_servers


@pytest.mark.asyncio
async def test_create_valid_sharing_group(db: Session, site_admin_user_token, instance_owner_org, client) -> None:
    body = {"name": f"Test Sharing Group {uuid()}{time_ns()}", "description": "description", "releasability": "yes"}

    response = client.post("/sharing_groups", headers={"authorization": site_admin_user_token}, json=body)

    assert response.status_code == status.HTTP_201_CREATED
    json: dict = response.json()
    assert json["org_id"] == instance_owner_org.id
    assert json["organisation_uuid"] == instance_owner_org.uuid

    db_sharing_group_org: SharingGroupOrg = (
        (await db.execute(select(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == json["id"])))
        .scalars()
        .first()
    )
    db_sharing_group_server: SharingGroupServer = (
        (await db.execute(select(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == json["id"])))
        .scalars()
        .first()
    )
    ic(db_sharing_group_org.asdict())
    assert db_sharing_group_org.org_id == instance_owner_org.id
    assert db_sharing_group_server

    await delete_sharing_group(db, json["id"])
    await delete_sharing_group_orgs(db, json["id"])
    await delete_sharing_group_server(db, json["id"])


@pytest.mark.asyncio
async def test_create_valid_sharing_group_with_org_id_overwrite(
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
    assert json["org_id"] == instance_two_owner_org.id
    assert json["organisation_uuid"] == instance_two_owner_org.uuid

    db_sharing_group_org: SharingGroupOrg = (
        (await db.execute(select(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == json["id"])))
        .scalars()
        .first()
    )
    db_sharing_group_server: SharingGroupServer = (
        (await db.execute(select(SharingGroupServer).filter(SharingGroupServer.sharing_group_id == json["id"])))
        .scalars()
        .first()
    )

    assert db_sharing_group_org.org_id == instance_two_owner_org.id
    assert db_sharing_group_server
    await delete_sharing_group(db, json["id"])
    await delete_sharing_group_orgs(db, json["id"])
    await delete_sharing_group_server(db, json["id"])


@pytest.mark.asyncio
async def test_create_sharing_group_with_org_id_overwrite_but_not_enough_permissions(
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
    assert json["org_id"] == instance_owner_org.id
    assert json["organisation_uuid"] == instance_owner_org.uuid

    await delete_sharing_group(db, json["id"])
    await delete_sharing_group_orgs(db, json["id"])
    await delete_sharing_group_server(db, json["id"])


@pytest.mark.asyncio
async def test_get_own_created_sharing_group(
    db: Session, sharing_group, instance_owner_org, instance_owner_org_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == sharing_group.id


@pytest.mark.asyncio
async def test_get_sharing_group_with_access_through_sharing_group_org(
    db: Session, sharing_group, sharing_group_org_two, instance_org_two_admin_user_token, client
) -> None:
    assert sharing_group_org_two

    response = client.get(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == sharing_group.id


@pytest.mark.asyncio
async def test_get_sharing_group_with_access_through_sharing_group_server(
    db: Session, sharing_group, sharing_group_server_all_orgs, instance_org_two_admin_user_token, client
) -> None:
    assert sharing_group
    assert sharing_group_server_all_orgs
    sharing_group_server_all_orgs.server_id = 0
    await db.commit()
    response = client.get(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == sharing_group.id


@pytest.mark.asyncio
async def test_get_sharing_group_with_access_through_site_admin(
    db: Session, sharing_group, site_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == sharing_group.id


@pytest.mark.asyncio
async def test_get_sharing_group_with_no_access(
    db: Session, sharing_group, sharing_group_server, instance_org_two, instance_org_two_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )
    ic(instance_org_two.asdict())
    ic(response.json())

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_own_sharing_group(
    db: Session, sharing_group, instance_owner_org_admin_user_token, client
) -> None:
    new_description = f"this is a new description + {datetime.utcnow()}"

    response = client.put(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": instance_owner_org_admin_user_token},
        json={"description": new_description},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == sharing_group.id
    assert json["uuid"] == sharing_group.uuid
    assert json["name"] == sharing_group.name
    assert json["description"] == new_description


@pytest.mark.asyncio
async def test_update_sharing_group_with_access_through_site_admin(
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
    assert json["id"] == sharing_group.id
    assert json["uuid"] == sharing_group.uuid
    assert json["name"] == sharing_group.name
    assert json["description"] == new_description


@pytest.mark.asyncio
async def test_update_sharing_group_no_access_although_sharing_group_org_exists(
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


@pytest.mark.asyncio
async def test_delete_own_sharing_group(
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
    assert json["id"] == sharing_group_id

    await db.invalidate()

    db_sharing_group: SharingGroup | None = await db.get(SharingGroup, sharing_group_id)
    db_sharing_group_org: SharingGroupOrg | None = await db.get(SharingGroupOrg, sharing_group_org_id)
    db_sharing_group_server: SharingGroupServer | None = await db.get(SharingGroupServer, sharing_group_server_id)

    assert not db_sharing_group
    assert not db_sharing_group_org
    assert not db_sharing_group_server

    second_response = client.delete(
        f"/sharing_groups/{sharing_group_id}",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert second_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_sharing_group_with_access_through_site_admin(
    db: Session, sharing_group, instance_org_two, site_admin_user_token, client
) -> None:
    response = client.delete(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == sharing_group.id

    second_response = client.delete(
        f"/sharing_groups/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
    )

    assert second_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_sharing_group_no_access_although_sharing_group_org_exists(
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


@pytest.mark.asyncio
async def test_list_own_sharing_group(db: Session, sharing_group, instance_owner_org_admin_user_token, client) -> None:
    response = client.get(
        "/sharing_groups",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    ic(json)
    sharing_group_items = [item for item in json["response"] if item["SharingGroup"]["id"] == sharing_group.id]
    sharing_group_item = sharing_group_items[0]

    assert sharing_group_item
    assert sharing_group_item["editable"]
    assert sharing_group_item["deletable"]


@pytest.mark.asyncio
async def test_list_own_sharing_group_site_admin(
    db: Session, sharing_group, instance_owner_org, site_admin_user_token, client
) -> None:
    response = client.get(
        "/sharing_groups",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    sharing_group_item = next(
        (item for item in json["response"] if item["SharingGroup"]["id"] == sharing_group.id), None
    )

    assert sharing_group_item
    assert sharing_group_item["editable"]
    assert sharing_group_item["deletable"]


@pytest.mark.asyncio
async def test_list_sharing_group_with_access_through_sharing_group_org(
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
        item for item in json["response"] if item["SharingGroup"]["id"] == sharing_group_org_two.sharing_group_id
    ]
    ic(sharing_group_items, sharing_group_org_two.id)
    sharing_group_item = sharing_group_items[0]

    assert sharing_group_item
    assert sharing_group_item["SharingGroupOrg"][0]["Organisation"]
    assert not sharing_group_item["editable"]
    assert not sharing_group_item["deletable"]


@pytest.mark.asyncio
async def test_list_sharing_group_with_access_through_sharing_group_server(
    db: Session,
    sharing_group,
    sharing_group_server_all_orgs,
    instance_org_two_admin_user_token,
    site_admin_user_token,
    client,
) -> None:
    assert sharing_group_server_all_orgs

    sharing_group_server_all_orgs.server_id = 0
    await db.commit()

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
    sharing_group_items = [item for item in json["response"] if item["SharingGroup"]["id"] == sharing_group.id]
    sharing_group_item = sharing_group_items[0]

    assert sharing_group_item
    assert sharing_group_item["SharingGroupServer"][0]["Server"]["id"] == "0"
    assert not sharing_group_item["editable"]
    assert not sharing_group_item["deletable"]


@pytest.mark.asyncio
async def test_list_sharing_group_with_no_access(
    db: Session, sharing_group, sharing_group_server, instance_org_two, instance_org_two_admin_user_token, client
) -> None:
    response = client.get(
        "/sharing_groups",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    sharing_group_item = next(
        (item for item in json["response"] if item["SharingGroup"]["id"] == sharing_group.id), None
    )

    assert not sharing_group_item


@pytest.mark.asyncio
async def test_get_own_created_sharing_group_info(
    db: Session, sharing_group, instance_owner_org_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/{sharing_group.id}/info",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    assert json["SharingGroup"]["id"] == sharing_group.id
    assert json["SharingGroup"]["org_count"] == 0


@pytest.mark.asyncio
async def test_get_sharing_group_info_with_access_through_sharing_group_org(
    sharing_group, sharing_group_org_two, instance_org_two_admin_user_token, client
) -> None:
    assert sharing_group_org_two
    response = client.get(
        f"/sharing_groups/{sharing_group.id}/info",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    assert json["SharingGroup"]["id"] == sharing_group.id
    assert json["SharingGroup"]["org_count"] == 1


@pytest.mark.asyncio
async def test_get_sharing_group_info_with_access_through_sharing_group_server(
    db, sharing_group, sharing_group_server_all_orgs, instance_org_two_admin_user_token, client
) -> None:
    sharing_group_server_all_orgs.server_id = 0
    await db.commit()

    assert sharing_group_server_all_orgs
    response = client.get(
        f"/sharing_groups/{sharing_group.id}/info",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    assert json["SharingGroup"]["id"] == sharing_group.id
    assert json["SharingGroup"]["org_count"] == 0


@pytest.mark.asyncio
async def test_get_sharing_group_info_with_access_through_site_admin(
    db: Session, site_admin_user_token, sharing_group, client
) -> None:
    response = client.get(
        f"/sharing_groups/{sharing_group.id}/info",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()

    assert json["SharingGroup"]["id"] == sharing_group.id
    assert json["SharingGroup"]["org_count"] == 0


@pytest.mark.asyncio
async def test_get_sharing_group_info_with_no_access(
    db: Session, sharing_group_server, sharing_group, instance_org_two, instance_org_two_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/{sharing_group.id}/info",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_add_org_to_own_sharing_group(
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
    assert json["org_id"] == 999
    await delete_sharing_group_orgs(db, sharing_group.id)


@pytest.mark.asyncio
async def test_patch_org_to_own_sharing_group(
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
    assert json["org_id"] == 999
    assert json["extend"]

    await delete_sharing_group_orgs(db, sharing_group.id)


@pytest.mark.asyncio
async def test_add_org_to_sharing_group_using_site_admin(
    db: Session, instance_org_two, site_admin_user_token, sharing_group, client
) -> None:
    response = client.patch(
        f"/sharing_groups/{sharing_group.id}/organisations",
        headers={"authorization": site_admin_user_token},
        json={"organisationId": "999"},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["sharing_group_id"] == sharing_group.id

    await delete_sharing_group_orgs(db, sharing_group.id)


@pytest.mark.asyncio
async def test_add_org_to_sharing_group_with_no_access(
    db: Session, sharing_group2, sharing_group_org, instance_owner_org, instance_owner_org_admin_user_token, client
) -> None:
    response = client.patch(
        f"/sharing_groups/{sharing_group2.id}/organisations",
        headers={"authorization": instance_owner_org_admin_user_token},
        json={"organisationId": "999"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_remove_org_from_own_sharing_group(
    db: Session, instance_owner_org, sharing_group, sharing_group_org, instance_owner_org_admin_user_token, client
) -> None:
    sharing_group_org_id = sharing_group_org.id

    response = client.delete(
        f"/sharing_groups/{sharing_group.id}/organisations/{instance_owner_org.id}",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK

    await db.invalidate()

    db_sharing_group_org = await db.get(SharingGroupOrg, sharing_group_org_id)

    assert not db_sharing_group_org


@pytest.mark.asyncio
async def test_add_server_to_own_sharing_group(db, sharing_group, instance_owner_org_admin_user_token, client) -> None:
    response = client.patch(
        f"/sharing_groups/{sharing_group.id}/servers",
        headers={"authorization": instance_owner_org_admin_user_token},
        json={"serverId": "999"},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["sharing_group_id"] == sharing_group.id

    await delete_sharing_group_server(db, sharing_group.id)


@pytest.mark.asyncio
async def test_patch_server_to_own_sharing_group(
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
    assert json["server_id"] == 999
    assert json["all_orgs"]

    await delete_sharing_group_server(db, sharing_group.id)


@pytest.mark.asyncio
async def test_add_server_to_sharing_group_using_site_admin(
    db: Session, sharing_group, site_admin_user_token, client
) -> None:
    response = client.patch(
        f"/sharing_groups/{sharing_group.id}/servers",
        headers={"authorization": site_admin_user_token},
        json={"serverId": "999"},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["sharing_group_id"] == sharing_group.id
    await delete_sharing_group_server(db, sharing_group.id)


@pytest.mark.asyncio
async def test_add_server_to_sharing_group_with_no_access(
    db: Session, sharing_group, sharing_group_org, instance_owner_org, instance_org_two_admin_user_token, client
) -> None:
    response = client.patch(
        f"/sharing_groups/{sharing_group.id}/servers",
        headers={"authorization": instance_org_two_admin_user_token},
        json={"serverId": "999"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_remove_server_from_own_sharing_group(
    db, sharing_group_server, sharing_group, instance_owner_org_admin_user_token, client
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

    await db.invalidate()

    db_sharing_group_server = await db.get(SharingGroupServer, sharing_group_server_id)

    assert not db_sharing_group_server


@pytest.mark.asyncio
async def test_create_valid_sharing_group_legacy(db, instance_owner_org, site_admin_user_token, client) -> None:
    body = {"name": f"Test Sharing Group {uuid()}{time_ns()}", "description": "description", "releasability": "yes"}

    response = client.post("/sharing_groups/add", headers={"authorization": site_admin_user_token}, json=body)

    assert response.status_code == status.HTTP_201_CREATED
    json: dict = response.json()
    assert json["SharingGroup"]["org_id"] == instance_owner_org.id
    assert json["SharingGroup"]["organisation_uuid"] == instance_owner_org.uuid
    assert json["SharingGroupOrg"][0]["org_id"] == instance_owner_org.id
    assert json["SharingGroupServer"][0]["server_id"] == 0

    ic(json)
    db_sharing_group_org: SharingGroupOrg = (
        (
            await db.execute(
                select(SharingGroupOrg).filter(SharingGroupOrg.sharing_group_id == json["SharingGroup"]["id"])
            )
        )
        .scalars()
        .first()
    )
    await db.delete(db_sharing_group_org)
    await db.commit()
    await delete_sharing_group(db, json["SharingGroup"]["id"])
    await delete_sharing_group_server(db, json["SharingGroup"]["id"])


@pytest.mark.asyncio
async def test_create_valid_sharing_group_legacy_with_org_id_overwrite(
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
    assert json["SharingGroup"]["org_id"] == instance_two_owner_org.id
    assert json["SharingGroup"]["organisation_uuid"] == instance_two_owner_org.uuid
    assert json["SharingGroupOrg"][0]["org_id"] == instance_two_owner_org.id
    assert json["SharingGroupServer"][0]["server_id"] == 0

    await delete_sharing_group(db, json["SharingGroup"]["id"])
    await delete_sharing_group_orgs(db, json["SharingGroup"]["id"])
    await delete_sharing_group_server(db, json["SharingGroup"]["id"])


@pytest.mark.asyncio
async def test_create_sharing_group_legacy_with_org_id_overwrite_but_not_enough_permissions(
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
    assert json["SharingGroup"]["org_id"] == instance_owner_org.id
    assert json["SharingGroup"]["organisation_uuid"] == instance_owner_org.uuid
    assert json["SharingGroupOrg"][0]["org_id"] == instance_owner_org.id
    assert json["SharingGroupServer"][0]["server_id"] == 0

    await delete_sharing_group(db, json["SharingGroup"]["id"])
    await delete_sharing_group_orgs(db, json["SharingGroup"]["id"])
    await delete_sharing_group_server(db, json["SharingGroup"]["id"])


@pytest.mark.asyncio
async def test_get_own_created_sharing_group_legacy(
    db: Session, sharing_group, instance_owner_org_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/view/{sharing_group.id}",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["SharingGroup"]["id"] == sharing_group.id


@pytest.mark.asyncio
async def test_get_sharing_group_legacy_with_access_through_sharing_group_org(
    db: Session, sharing_group, sharing_group_org_two, instance_org_two_admin_user_token, client
) -> None:
    assert sharing_group_org_two

    response = client.get(
        f"/sharing_groups/view/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["SharingGroup"]["id"] == sharing_group.id


@pytest.mark.asyncio
async def test_get_sharing_group_legacy_with_access_through_sharing_group_server(
    db, sharing_group, sharing_group_server_all_orgs, instance_org_two_admin_user_token, client
) -> None:
    assert sharing_group_server_all_orgs
    sharing_group_server_all_orgs.server_id = 0
    await db.commit()

    response = client.get(
        f"/sharing_groups/view/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["SharingGroup"]["id"] == sharing_group.id


@pytest.mark.asyncio
async def test_get_sharing_group_legacy_with_access_through_site_admin(
    db: Session, sharing_group, instance_org_two, site_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/view/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["SharingGroup"]["id"] == sharing_group.id


@pytest.mark.asyncio
async def test_get_sharing_group_legacy_with_no_access(
    db: Session, sharing_group, sharing_group_server, instance_org_two_admin_user_token, client
) -> None:
    response = client.get(
        f"/sharing_groups/view/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_own_sharing_group_legacy(
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
    assert json["SharingGroup"]["id"] == sharing_group.id
    assert json["SharingGroup"]["uuid"] == sharing_group.uuid
    assert json["SharingGroup"]["name"] == sharing_group.name
    assert json["SharingGroup"]["description"] == new_description


@pytest.mark.asyncio
async def test_update_sharing_group_legacy_with_access_through_site_admin(
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
    assert json["SharingGroup"]["id"] == sharing_group.id
    assert json["SharingGroup"]["uuid"] == sharing_group.uuid
    assert json["SharingGroup"]["name"] == sharing_group.name
    assert json["SharingGroup"]["description"] == new_description


@pytest.mark.asyncio
async def test_update_sharing_group_legacy_no_access_although_sharing_group_org_exists(
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


@pytest.mark.asyncio
async def test_delete_own_sharing_group_legacy(
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
    assert json["id"] == sharing_group.id
    assert json["saved"]
    assert json["success"]

    await db.invalidate()

    db_sharing_group: SharingGroup | None = await db.get(SharingGroup, sharing_group_id)
    db_sharing_group_org: SharingGroupOrg | None = await db.get(SharingGroupOrg, sharing_group_org_id)
    db_sharing_group_server: SharingGroupServer | None = await db.get(SharingGroupServer, sharing_group_server_id)

    assert not db_sharing_group
    assert not db_sharing_group_org
    assert not db_sharing_group_server

    second_response = client.delete(
        f"/sharing_groups/delete/{sharing_group_id}",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert second_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_sharing_group_legacy_with_access_through_site_admin(
    db: Session, sharing_group, instance_org_two, site_admin_user_token, client
) -> None:
    response = client.delete(
        f"/sharing_groups/delete/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["id"] == sharing_group.id
    assert json["saved"]
    assert json["success"]

    second_response = client.delete(
        f"/sharing_groups/delete/{sharing_group.id}",
        headers={"authorization": site_admin_user_token},
    )

    assert second_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_sharing_group_legacy_no_access_although_sharing_group_org_exists(
    db: Session, sharing_group, sharing_group_org, instance_owner_org, instance_org_two_admin_user_token, client
) -> None:
    response = client.delete(
        f"/sharing_groups/delete/{sharing_group.id}",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_add_org_to_own_sharing_group_legacy(
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

    await delete_sharing_group_orgs(db, sharing_group.id)


@pytest.mark.asyncio
async def test_patch_org_to_own_sharing_group_legacy(
    db: Session, sharing_group, sharing_group_org, instance_owner_org_admin_user_token, client
) -> None:
    sharing_group_org.extend = True
    await db.commit()
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

    await db.invalidate()

    db_sharing_group_org: SharingGroupOrg = await db.get(SharingGroupOrg, sharing_group_org_id)

    ic(db_sharing_group_org.asdict())
    assert db_sharing_group_org.extend

    await delete_sharing_group_server(db, sharing_group.id)
    await delete_sharing_group_orgs(db, sharing_group.id)


@pytest.mark.asyncio
async def test_add_org_to_sharing_group_legacy_using_site_admin(
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

    await delete_sharing_group_orgs(db, sharing_group.id)


@pytest.mark.asyncio
async def test_add_org_to_sharing_group_legacy_with_no_access(
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


@pytest.mark.asyncio
async def test_remove_org_from_own_sharing_group_legacy(
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

    await db.invalidate()

    db_sharing_group_org = await db.get(SharingGroupOrg, sharing_group_org_id)

    assert not db_sharing_group_org


@pytest.mark.asyncio
async def test_add_server_to_own_sharing_group_legacy(
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

    await delete_sharing_group_server(db, sharing_group.id)


@pytest.mark.asyncio
async def test_patch_server_to_own_sharing_group_legacy(
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

    await db.invalidate()

    db_sharing_group_server: SharingGroupServer = await db.get(SharingGroupServer, sharing_group_server_id)

    assert db_sharing_group_server.all_orgs
    await delete_sharing_group_server(db, sharing_group.id)


@pytest.mark.asyncio
async def test_add_server_to_sharing_group_legeacy_using_site_admin(
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

    await delete_sharing_group_server(db, sharing_group.id)


@pytest.mark.asyncio
async def test_add_server_to_sharing_group_legacy_with_no_access(
    db: Session, sharing_group, instance_owner_org, sharing_group_org, instance_org_two_admin_user_token, client
) -> None:
    response = client.post(
        f"/sharing_groups/addServer/{sharing_group.id}/999",
        headers={"authorization": instance_org_two_admin_user_token},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_remove_server_from_own_sharing_group_legacy(
    db: Session, sharing_group, sharing_group_server, instance_owner_org, instance_owner_org_admin_user_token, client
) -> None:
    sharing_group_server_id = sharing_group_server.id

    response = client.post(
        f"/sharing_groups/removeServer/{sharing_group.id}/{sharing_group_server.server_id}",
        headers={"authorization": instance_owner_org_admin_user_token},
    )

    assert response.status_code == status.HTTP_200_OK

    await db.invalidate()

    db_sharing_group_server = await db.get(SharingGroupServer, sharing_group_server_id)

    assert not db_sharing_group_server
