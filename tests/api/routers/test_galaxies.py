import pytest
import sqlalchemy as sa
from icecream import ic
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from mmisp.api_schemas.galaxies import ExportGalaxyAttributes, ExportGalaxyBody
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement, GalaxyReference

from ...generators.model_generators.galaxy_generator import generate_galaxy
from ...generators.model_generators.organisation_generator import generate_organisation
from ..helpers.galaxy_helper import get_invalid_import_galaxy_body, get_valid_import_galaxy_body


@pytest.fixture(autouse=True)
def check_counts_stay_constant(db):
    count_galaxies = db.execute(text("SELECT COUNT(*) FROM galaxies")).first()[0]
    count_galaxy_clusters = db.execute(text("SELECT COUNT(*) FROM galaxy_clusters")).first()[0]
    count_galaxy_elements = db.execute(text("SELECT COUNT(*) FROM galaxy_elements")).first()[0]
    yield
    ncount_galaxies = db.execute(text("SELECT COUNT(*) FROM galaxies")).first()[0]
    ncount_galaxy_clusters = db.execute(text("SELECT COUNT(*) FROM galaxy_clusters")).first()[0]
    ncount_galaxy_elements = db.execute(text("SELECT COUNT(*) FROM galaxy_elements")).first()[0]

    assert count_galaxies == ncount_galaxies
    assert count_galaxy_clusters == ncount_galaxy_clusters
    assert count_galaxy_elements == ncount_galaxy_elements


@pytest.fixture
def galaxy(db):
    galaxy = generate_galaxy()

    db.add(galaxy)
    db.commit()
    db.refresh(galaxy)

    yield galaxy

    db.delete(galaxy)
    db.commit()


@pytest.fixture
def galaxy2(db):
    galaxy = generate_galaxy()

    db.add(galaxy)
    db.commit()
    db.refresh(galaxy)

    yield galaxy

    db.delete(galaxy)
    db.commit()


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
def add_galaxy_cluster_body(db, galaxy, tag):
    add_galaxy_cluster_body = GalaxyCluster(
        type="test", value="test", tag_name=tag.name, description="", galaxy_id=galaxy.id, authors="Me"
    )

    db.add(add_galaxy_cluster_body)
    db.commit()
    db.refresh(add_galaxy_cluster_body)

    yield add_galaxy_cluster_body

    db.delete(add_galaxy_cluster_body)
    db.commit()


@pytest.fixture
def add_galaxy_cluster_body2(db, galaxy2, tag):
    add_galaxy_cluster_body = GalaxyCluster(
        type="test", value="test", tag_name=tag.name, description="", galaxy_id=galaxy2.id, authors="Me"
    )

    db.add(add_galaxy_cluster_body)
    db.commit()
    db.refresh(add_galaxy_cluster_body)

    yield add_galaxy_cluster_body

    db.delete(add_galaxy_cluster_body)
    db.commit()


@pytest.fixture
def add_galaxy_element(db, add_galaxy_cluster_body):
    add_galaxy_element = GalaxyElement(
        galaxy_cluster_id=add_galaxy_cluster_body.id, key="refs", value="http://github.com"
    )

    db.add(add_galaxy_element)
    db.commit()
    db.refresh(add_galaxy_element)

    yield add_galaxy_element

    db.delete(add_galaxy_element)
    db.commit()


def test_import_galaxy_cluster_valid_data(db, site_admin_user_token, galaxy, organisation, tag, client) -> None:
    org_id = organisation.id
    galaxy_id = galaxy.id
    tag_name = tag.name

    request_body = get_valid_import_galaxy_body(tag_name, galaxy_id, org_id, galaxy.uuid)

    headers = {"authorization": site_admin_user_token}
    response = client.post("/galaxies/import", json=request_body, headers=headers)
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["name"] == "Galaxy clusters imported. 1 imported, 0 ignored, 0 failed."

    ic(response_json)
    ic(request_body)
    stmt = sa.sql.text(
        "DELETE FROM galaxy_elements WHERE galaxy_cluster_id IN (SELECT id FROM galaxy_clusters WHERE galaxy_id=:id)"
    )
    db.execute(stmt, {"id": galaxy_id})

    stmt = sa.sql.text("DELETE FROM galaxy_clusters WHERE galaxy_id=:id")
    db.execute(stmt, {"id": galaxy_id})
    db.commit()


def test_import_galaxy_cluster_invalid_data(site_admin_user_token, galaxy, organisation, tag, client) -> None:
    org_id = organisation.id
    galaxy_id = galaxy.id
    tag_name = tag.name

    request_body = get_invalid_import_galaxy_body(tag_name, galaxy_id, org_id)

    headers = {"authorization": site_admin_user_token}
    response = client.post("/galaxies/import", json=request_body, headers=headers)

    assert response.status_code == 403


def test_get_existing_galaxy_cluster(db: Session, site_admin_user_token, galaxy, add_galaxy_cluster_body, client
) -> None:
    galaxy_id = galaxy.id
    galaxy_cluster_id = add_galaxy_cluster_body.id

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/galaxies/clusters/{galaxy_cluster_idD}", headers=headers)

    assert response.status_code == 200

    response_json = response.json()

    assert response_json["id"] == str(cluster_id)
    assert response_json["galaxy_id"] == str(galaxy_id)
    assert response_json["type"] == add_galaxy_cluster_body.type
    assert response_json["value"] == add_galaxy_cluster_body.value
    assert response_json["tag_name"] == add_galaxy_cluster_body.tag_name


def test_get_non_existing_galaxy_cluster(site_admin_user_token, client
) -> None:

    headers = {"authorization": site_admin_user_token}
    response = client.get("/galaxies/clusters/0", headers=headers)
    assert response.status_code == 404
    response = client.get("/events/invalid_id", headers=headers)
    assert response.status_code == 404


def test_get_existing_galaxy_details(
    db: Session, site_admin_user_token, galaxy, add_galaxy_cluster_body, add_galaxy_element, client
) -> None:
    galaxy_id = galaxy.id
    galaxy_cluster_id = add_galaxy_cluster_body.id

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/galaxies/{galaxy_id}", headers=headers)

    assert response.status_code == 200

    response_json = response.json()

    ic(response_json)
    assert response_json["Galaxy"]["id"] == str(galaxy_id)
    assert len(response_json["GalaxyCluster"]) == 1
    assert response_json["GalaxyCluster"][0]["id"] == str(galaxy_cluster_id)
    assert response_json["GalaxyCluster"][0]["GalaxyElement"][0]["id"] == str(add_galaxy_element.id)
    assert response_json["GalaxyCluster"][0]["GalaxyElement"][0]["key"] == add_galaxy_element.key
    assert response_json["GalaxyCluster"][0]["GalaxyElement"][0]["value"] == add_galaxy_element.value


def test_get_non_existing_galaxy_details(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/galaxies/0", headers=headers)

    assert response.status_code == 404


def test_delete_existing_galaxy(
    db: Session, site_admin_user_token, galaxy, organisation, tag, add_galaxy_cluster_body, add_galaxy_element, client
) -> None:
    galaxy_id = galaxy.id

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/galaxies/{galaxy_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["name"] == "Galaxy deleted"


def test_delete_non_existing_galaxy(site_admin_user_token, galaxy, organisation, tag, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete("/galaxies/0", headers=headers)

    assert response.status_code == 404
    response_json = response.json()
    print(response_json)
    assert response_json["detail"]["name"] == "Invalid galaxy."


def test_get_all_galaxies(
    db: Session, site_admin_user_token, add_galaxy_cluster_body, add_galaxy_cluster_body2, client
) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/galaxies", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)


def test_search_galaxies(site_admin_user_token, organisation, tag, galaxy, client) -> None:
    request_body = {"value": "test galaxy single name abcdefghijklmnopqrstuvwxyz"}

    headers = {"authorization": site_admin_user_token}
    response = client.post("/galaxies", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    for galaxy in response_json:
        assert galaxy["Galaxy"]["name"] == request_body["name"]


def test_export_existing_galaxy(
    db: Session,
    site_admin_user_token,
    galaxy,
    organisation,
    tag,
    add_galaxy_cluster_body,
    add_galaxy_cluster_body2,
    add_galaxy_element,
    client,
) -> None:
    galaxy_id = galaxy.id

    galaxy_cluster_id1 = add_galaxy_cluster_body.id
    galaxy_cluster_id = add_galaxy_cluster_body2.id
    assert galaxy_cluster_id

    galaxy_reference = GalaxyReference(
        galaxy_cluster_id=galaxy_cluster_id1,
        referenced_galaxy_cluster_id=add_galaxy_cluster_body.id,
        referenced_galaxy_cluster_uuid=add_galaxy_cluster_body.uuid,
        referenced_galaxy_cluster_type=add_galaxy_cluster_body.type,
        referenced_galaxy_cluster_value=add_galaxy_cluster_body.value,
    )

    db.add(galaxy_reference)
    db.commit()
    db.refresh(galaxy_reference)

    body = ExportGalaxyBody(Galaxy=ExportGalaxyAttributes(default=False, distribution="1"))
    request_body = body.dict()

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/galaxies/export/{galaxy_id}", json=request_body, headers=headers)

    assert response.status_code == 200


def test_export_non_existing_galaxy(
    db: Session,
    site_admin_user_token,
    galaxy,
    organisation,
    tag,
    add_galaxy_cluster_body,
    add_galaxy_cluster_body2,
    add_galaxy_element,
    client,
) -> None:
    galaxy_cluster_id1 = add_galaxy_cluster_body.id

    galaxy_reference = GalaxyReference(
        galaxy_cluster_id=galaxy_cluster_id1,
        referenced_galaxy_cluster_id=add_galaxy_cluster_body.id,
        referenced_galaxy_cluster_uuid=add_galaxy_cluster_body.uuid,
        referenced_galaxy_cluster_type=add_galaxy_cluster_body.type,
        referenced_galaxy_cluster_value=add_galaxy_cluster_body.value,
    )

    db.add(galaxy_reference)
    db.commit()
    db.refresh(galaxy_reference)

    body = ExportGalaxyBody(Galaxy=ExportGalaxyAttributes(default=False, distribution="1"))
    request_body = body.dict()
    headers = {"authorization": site_admin_user_token}
    response = client.post("/galaxies/export/0", json=request_body, headers=headers)

    assert response.status_code == 404


def test_attach_cluster(
    site_admin_user_token, galaxy, organisation, tag, add_galaxy_cluster_body, event, client
) -> None:
    galaxy_cluster_id1 = add_galaxy_cluster_body.id
    event_id = event.id

    headers = {"authorization": site_admin_user_token}

    request_body = {"Galaxy": {"target_id": galaxy_cluster_id1}}
    response = client.post(f"/galaxies/attachCluster/{event_id}/event/local:0", json=request_body, headers=headers)

    assert response.status_code == 200
    assert response.json()["success"] == "Cluster attached."


def test_attach_cluster_non_existing_cluster(site_admin_user_token, client) -> None:
    request_body = {"Galaxy": {"target_id": 0}}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/galaxies/attachCluster/1/event/local:0", json=request_body, headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid Galaxy cluster."
