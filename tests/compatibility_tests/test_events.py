import pytest
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


async def delete_event(db, id):
    stmt = sa.sql.text("DELETE FROM events WHERE id=:id")
    result = await db.execute(stmt, {"id": id})
    await db.commit()
    assert result.rowcount == 1


@pytest.mark.asyncio
async def test_view_event_normal_attribute_tag(db, event, attribute_with_normal_tag, auth_key, client) -> None:
    assert get_legacy_modern_diff("get", f"/events/view/{event.id}?extended=true", {}, auth_key, client) == {}


@pytest.mark.asyncio
async def test_view_event_galaxy_cluster_tag(
    db: AsyncSession, event, attribute_with_galaxy_cluster_one_tag, auth_key, client
) -> None:
    assert get_legacy_modern_diff("get", f"/events/view/{event.id}", {}, auth_key, client) == {}


"""
@pytest.mark.asyncio
async def test_add_event_valid_data(
    db,
    instance_owner_org,
    auth_key,
    client,
) -> None:
    def preprocessor(modern, legacy):
        del modern["Event"]["timestamp"]
        del legacy["Event"]["timestamp"]
        del modern["Event"]["uuid"]
        del legacy["Event"]["uuid"]
        del modern["Event"]["id"]
        del legacy["Event"]["id"]

    path = "/events"
    request_body = {"info": "test events", "distribution": 0, "sharing_group_id": 0,
                    "org_id": instance_owner_org.id,
                    "orgc_id": instance_owner_org.id}

    assert get_legacy_modern_diff("post", path, request_body, auth_key, client, preprocessor) == {}



@pytest.mark.asyncio
async def test_add_event_data_empty_string(db, site_admin_user_token, instance_owner_org, auth_key, client) -> None:
    def preprocessor(modern, legacy):
        del modern["Event"]["timestamp"]
        del legacy["Event"]["timestamp"]
        del modern["Event"]["uuid"]
        del legacy["Event"]["uuid"]
        del modern["Event"]["id"]
        del legacy["Event"]["id"]

    path = "/events"
    request_body = {"info": "test events", "date": "", "distribution": 0, "sharing_group_id": 0,
                    "org_id": instance_owner_org.id,
                    "orgc_id": instance_owner_org.id
                    }

    #response = client.post(path, json=request_body, headers={"Authorization": site_admin_user_token})
    #assert response.status_code == 200
    #event_id = response.json()["Event"]["id"]
    #assert event_id is not None
    #event2_id = int(event_id) + 1
    assert get_legacy_modern_diff("post", path, request_body, auth_key, client, preprocessor) == {}

    #delete_response = client.delete(f"events/{event_id}", headers={"Authorization": site_admin_user_token})
    #assert delete_response.status_code == 200
    #delete_diff = client.delete(f"events/{event2_id}", headers={"Authorization": site_admin_user_token})
    #assert delete_diff.status_code == 200
"""


@pytest.mark.asyncio
async def test_get_existing_event(db, auth_key, client, event) -> None:
    path = f"/events/{event.id}"

    request_body = {}

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_get_non_existing_event(db, auth_key, client) -> None:
    path = f"/events/{9999}"

    request_body = {}

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_update_existing_event(db, auth_key, client, event) -> None:
    def preprocessor(modern, legacy):
        del modern["Event"]["timestamp"]
        del legacy["Event"]["timestamp"]

    path = f"/events/{event.id}"

    request_body = {"info": "updated info"}

    assert get_legacy_modern_diff("put", path, request_body, auth_key, client, preprocessor) == {}


@pytest.mark.asyncio
async def test_update_non_existing_event(db, auth_key, client) -> None:
    path = f"/events/{9999}"

    request_body = {"info": "updated info"}

    assert get_legacy_modern_diff("put", path, request_body, auth_key, client) == {}


# @pytest.mark.asyncio
# async def test_delete_existing_event(db, auth_key, client, event) -> None:
#
#    path = f"/events/{event.id}"
#
#    request_body = None
#
#    assert get_legacy_modern_diff("delete", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_delete_non_existing_event(db, auth_key, client) -> None:
    path = f"/events/{9999}"

    request_body = None

    assert get_legacy_modern_diff("delete", path, request_body, auth_key, client) == {}
