import pytest
from icecream import ic


@pytest.mark.asyncio
async def test_get_statistics(
    client,
    event,
    event2,
    event3,
    event4,
    event5,
    site_admin_user,
    view_only_user,
    attribute,
    attribute2,
    attribute3,
    site_admin_user_token,
) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/statistics/getUsageData", headers=headers)
    response_json = response.json()
    assert response_json["users"] == 3
    assert response_json["eventCreatorOrgs"] == 1
    assert response_json["events"] == 5
    #    assert response_json["organisations"] == 2
    # assert response_json["localOrganisations"] <= 3
    assert response_json["attributes"] <= 3
    #    assert response_json["eventAttributes"] == 2 TODO: fixme
    #    assert response_json["usersWithGPGKeys"] == 1
    # assert response_json["averageUsersPerOrg"] == 1.0


@pytest.mark.asyncio
async def test_get_statistics_by_org_users(client, site_admin_user, site_admin_user_token):
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/statistics/getAttributes/{site_admin_user.org_id}", headers=headers)
    response_json = response.json()

    assert response_json["users"] == 1
    assert response_json["events"] == 0
    assert response_json["attributes"] == 0


@pytest.mark.asyncio
async def test_get_statistics_by_org_event_attribute(client, attribute, event, site_admin_user_token):
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/statistics/getAttributes/{event.org_id}", headers=headers)
    response_json = response.json()

    assert response_json["users"] == 0
    assert response_json["events"] == 1
    assert response_json["attributes"] == 1


@pytest.mark.asyncio
async def test_get_logincount(client, site_admin_user, site_admin_user_token):
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/statistics/logincount/{site_admin_user.org_id}", headers=headers)
    response_json = response.json()
    ic(response_json)
    assert True


#    assert response_json == 5 # TODO: fixme
