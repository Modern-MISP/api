from time import time

import pytest
import pytest_asyncio
from sqlalchemy.orm import Session

from mmisp.tests.generators.model_generators.organisation_generator import generate_organisation


@pytest_asyncio.fixture
async def organisation(db):
    organisation = generate_organisation()

    db.add(organisation)
    await db.commit()
    await db.refresh(organisation)

    yield organisation

    await db.delete(organisation)
    await db.commit()


@pytest_asyncio.fixture
async def organisation2(db):
    organisation = generate_organisation()

    db.add(organisation)
    await db.commit()
    await db.refresh(organisation)

    yield organisation

    await db.delete(organisation)
    await db.commit()


@pytest.mark.asyncio
async def test_get_organisation_by_id(db: Session, site_admin_user_token, client, organisation) -> None:
    org_id = organisation.id

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"organisations/{org_id}", headers=headers)

    assert response.status_code == 200

    response_json = response.json()

    assert response_json["id"] == org_id
    assert response_json["name"] == organisation.name
    assert response_json["description"] == organisation.description
    assert response_json["nationality"] == organisation.nationality
    assert response_json["sector"] == organisation.sector


@pytest.mark.asyncio
async def test_get_all_organisations(db: Session, site_admin_user_token, client, organisation, organisation2) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/organisations/all", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    response_json = response.json()
    print(response_json)
    for organisation in response_json:
        print(organisation)
        organisation_data = organisation["Organisation"]
        assert "id" in organisation_data
        assert "name" in organisation_data
        assert "description" in organisation_data
        assert "nationality" in organisation_data
        assert "sector" in organisation_data
        assert "user_count" in organisation_data


@pytest.mark.asyncio
async def test_delete_organisation(db: Session, site_admin_user_token, client, organisation) -> None:
    org_id = organisation.id

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/organisations/delete/{org_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["name"] == "Organisation deleted"


@pytest.mark.asyncio
async def test_add_organisation(client, site_admin_user_token, db: Session):
    name = "test" + str(time())
    headers = {"authorization": site_admin_user_token}
    request_body = {
        "id": 0,
        "name": name,
        "description": "des",
        "type": "typeA",
        "nationality": "world",
        "sector": "secA",
        "created_by": 0,
        "contacts": "contact",
        "local": True,
        "restricted_to_domain": "domain",
        "landingpage": "page",
    }

    response = client.post("/organisations", headers=headers, json=request_body)
    response_json = response.json()

    assert response_json["id"] == 0
    assert response_json["name"] == name


@pytest.mark.asyncio
async def test_edit_organisation(client, site_admin_user_token, organisation):
    headers = {"authorization": site_admin_user_token}
    request_body = {
        "name": "test1",
        "description": "des1",
        "type": "typeA1",
        "nationality": "world1",
        "sector": "secA1",
        "contacts": "contact1",
        "local": True,
        "restricted_to_domain": "domain1",
        "landingpage": "page1",
    }

    response = client.post(f"/organisations/update/{organisation.id}", headers=headers, json=request_body)
    response_json = response.json()
    assert response_json["name"] == "test1"
