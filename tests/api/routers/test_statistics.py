import pytest
import sqlalchemy as sa
from icecream import ic
from sqlalchemy.orm import Session

import datetime

from mmisp.db.models.event import Event
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.user import User

from ...generators.model_generators.attribute_generator import generate_attribute
from ...generators.model_generators.event_generator import generate_event

    
def test_get_statistics(client, 
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
                        site_admin_user_token
                        ) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/statistics/getUsageData", headers=headers)
    response_json = response.json()
    assert response_json["users"] == 2
    assert response_json["eventCreatorOrgs"] == 1
    assert response_json["events"] == 5
    assert response_json["organisations"] == 2
    assert response_json["localOrganisations"] == 2
    assert response_json["attributes"] == 2
    assert response_json["eventAttributes"] == 2
    assert response_json["usersWithGPGKeys"] == 1
    assert response_json["averageUsersPerOrg"] == 1.0

def test_get_statistics_by_org_users(client,
                              site_admin_user,
                              site_admin_user_token
                             ):
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/statistics/getAttributes/{site_admin_user.org_id}", headers=headers)
    response_json = response.json()

    assert response_json["users"] == 1
    assert response_json["events"] == 0
    assert response_json["attributes"] == 0

def test_get_statistics_by_org_event_attribute(client,
                              attribute,
                              event,
                              site_admin_user_token
                             ):
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/statistics/getAttributes/{event.org_id}", headers=headers)
    response_json = response.json()

    assert response_json["users"] == 0
    assert response_json["events"] == 1
    assert response_json["attributes"] == 1

def test_get_logincount(client,
                        site_admin_user,
                        site_admin_user_token
                        ):
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/statistics/logincount/{site_admin_user.org_id}", headers=headers)
    response_json = response.json()
    assert response_json == 5
