import pytest
import sqlalchemy as sa
from icecream import ic
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
import json
from time import time
from datetime import date

from icecream import ic
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from mmisp.db.models.organisation import Organisation
from mmisp.api_schemas.organisations import Organisation, AddOrganisation

from ...generators.model_generators.organisation_generator import generate_organisation


@pytest.fixture
def organisation(db):
    organisation = generate_organisation()

    db.add(organisation)
    db.commit()
    db.refresh(organisation)

    yield organisation

    db.delete(organisation)
    db.commit()


@pytest.fixture
def organisation2(db):
    organisation = generate_organisation()

    db.add(organisation)
    db.commit()
    db.refresh(organisation)

    yield organisation

    db.delete(organisation)
    db.commit()


def test_get_organisation_by_id(db: Session, site_admin_user_token, client, organisation) -> None:
    org_id = organisation.id

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"organisations/{org_id}", headers=headers)

    assert response.status_code == 200

    response_json = response.json()

    assert response_json["id"] == str(org_id)
    assert response_json["name"] == organisation.name
    assert response_json["description"] == organisation.description
    assert response_json["nationality"] == organisation.nationality
    assert response_json["sector"] == organisation.sector


def test_get_all_organisations(db: Session, site_admin_user_token, client, organisation, organisation2) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/organisations/all", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    response_json = response.json()
    for organisation in response_json:
        assert "id" in organisation
        assert "name" in organisation
        assert "description" in organisation
        assert "nationality" in organisation
        assert "sector" in organisation


def test_delete_organisation(db: Session, site_admin_user_token, client, organisation) -> None:
    org_id = organisation.id

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/organisations/delete/{org_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["name"] == "Organisation deleted"

