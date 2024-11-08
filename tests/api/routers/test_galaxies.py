import pytest
import pytest_asyncio
import sqlalchemy as sa
from icecream import ic
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from mmisp.api_schemas.galaxies import ExportGalaxyAttributes, ExportGalaxyBody
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement, GalaxyReference
from mmisp.tests.generators.model_generators.galaxy_generator import generate_galaxy
from mmisp.tests.generators.model_generators.organisation_generator import generate_organisation

from ..helpers.galaxy_helper import get_invalid_import_galaxy_body, get_valid_import_galaxy_body


@pytest_asyncio.fixture(autouse=True)
async def check_counts_stay_constant(db):
    count_galaxies = (await db.execute(text("SELECT COUNT(*) FROM galaxies"))).first()[0]
    count_galaxy_clusters = (await db.execute(text("SELECT COUNT(*) FROM galaxy_clusters"))).first()[0]
    count_galaxy_elements = (await db.execute(text("SELECT COUNT(*) FROM galaxy_elements"))).first()[0]
    yield
    ncount_galaxies = (await db.execute(text("SELECT COUNT(*) FROM galaxies"))).first()[0]
    ncount_galaxy_clusters = (await db.execute(text("SELECT COUNT(*) FROM galaxy_clusters"))).first()[0]
    ncount_galaxy_elements = (await db.execute(text("SELECT COUNT(*) FROM galaxy_elements"))).first()[0]

    assert count_galaxies == ncount_galaxies
    assert count_galaxy_clusters == ncount_galaxy_clusters
    assert count_galaxy_elements == ncount_galaxy_elements


@pytest_asyncio.fixture
async def galaxy(db):
    galaxy = generate_galaxy()

    db.add(galaxy)
    await db.commit()
    await db.refresh(galaxy)

    yield galaxy

    await db.delete(galaxy)
    await db.commit()


@pytest_asyncio.fixture
async def galaxy2(db):
    galaxy = generate_galaxy()

    db.add(galaxy)
    await db.commit()
    await db.refresh(galaxy)

    yield galaxy

    await db.delete(galaxy)
    await db.commit()


@pytest_asyncio.fixture
async def galaxy3(db):
    galaxy = generate_galaxy()

    db.add(galaxy)
    await db.commit()
    await db.refresh(galaxy)

    yield galaxy

    await db.delete(galaxy)
    await db.commit()


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
async def add_galaxy_cluster_body(db, galaxy, tag, organisation):
    add_galaxy_cluster_body = GalaxyCluster(
        type="test",
        value="test",
        tag_name=tag.name,
        description="",
        galaxy_id=galaxy.id,
        authors=["Me"],
        org_id=organisation.id,
        orgc_id=organisation.id,
        uuid="01ff063f-42de-49d7-9bbb-ef783d99fde7",
    )

    db.add(add_galaxy_cluster_body)
    await db.commit()
    await db.refresh(add_galaxy_cluster_body)

    yield add_galaxy_cluster_body

    await db.delete(add_galaxy_cluster_body)
    await db.commit()


@pytest_asyncio.fixture
async def add_galaxy_cluster_body2(db, galaxy2, tag, organisation):
    add_galaxy_cluster_body = GalaxyCluster(
        type="test",
        value="test",
        tag_name=tag.name,
        description="",
        galaxy_id=galaxy2.id,
        authors=["Me"],
        org_id=organisation.id,
        orgc_id=organisation.id,
        uuid="01ff063f-42de-49d7-9bbb-ef783d99fde8",
    )

    db.add(add_galaxy_cluster_body)
    await db.commit()
    await db.refresh(add_galaxy_cluster_body)

    yield add_galaxy_cluster_body

    await db.delete(add_galaxy_cluster_body)
    await db.commit()


@pytest_asyncio.fixture
async def add_galaxy_cluster_body3(db, galaxy3, tag, organisation):
    add_galaxy_cluster_body = GalaxyCluster(
        id="777",
        uuid="01ff063f-42de-49d7-9bbb-ef783d99fde9",
        collection_uuid="777",
        type="test",
        value="test",
        tag_name=tag.name,
        description="",
        galaxy_id=galaxy3.id,
        authors=["Me"],
        version="1.0",
        distribution="187",
        sharing_group_id="777",
        org_id=organisation.id,
        orgc_id=organisation.id,
        default=True,
        locked=False,
        extends_uuid="777",
        extends_version="777",
        published=True,
        deleted=False,
    )

    db.add(add_galaxy_cluster_body)
    await db.commit()
    await db.refresh(add_galaxy_cluster_body)

    yield add_galaxy_cluster_body

    await db.delete(add_galaxy_cluster_body)
    await db.commit()


@pytest_asyncio.fixture
async def add_galaxy_element(db, add_galaxy_cluster_body):
    add_galaxy_element = GalaxyElement(
        galaxy_cluster_id=add_galaxy_cluster_body.id, key="refs", value="http://github.com"
    )

    db.add(add_galaxy_element)
    await db.commit()
    await db.refresh(add_galaxy_element)

    yield add_galaxy_element

    await db.delete(add_galaxy_element)
    await db.commit()


@pytest_asyncio.fixture
async def add_galaxy_element2(db, add_galaxy_cluster_body3):
    add_galaxy_element = GalaxyElement(
        galaxy_cluster_id=add_galaxy_cluster_body3.id, key="refs", value="http://github.com"
    )

    db.add(add_galaxy_element)
    await db.commit()
    await db.refresh(add_galaxy_element)

    yield add_galaxy_element

    await db.delete(add_galaxy_element)
    await db.commit()


@pytest.mark.asyncio
async def test_import_galaxy_cluster_valid_data(db, site_admin_user_token, galaxy, organisation, tag, client) -> None:
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
    await db.execute(stmt, {"id": galaxy_id})

    stmt = sa.sql.text("DELETE FROM galaxy_clusters WHERE galaxy_id=:id")
    await db.execute(stmt, {"id": galaxy_id})
    await db.commit()


@pytest.mark.asyncio
async def test_import_galaxy_cluster_invalid_data(site_admin_user_token, galaxy, organisation, tag, client) -> None:
    org_id = organisation.id
    galaxy_id = galaxy.id
    tag_name = tag.name

    request_body = get_invalid_import_galaxy_body(tag_name, galaxy_id, org_id)

    headers = {"authorization": site_admin_user_token}
    response = client.post("/galaxies/import", json=request_body, headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_existing_galaxy_cluster(
    db: Session, site_admin_user_token, galaxy3, add_galaxy_cluster_body3, client
) -> None:
    galaxy_id = galaxy3.id
    galaxy_cluster_id = add_galaxy_cluster_body3.id

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/galaxies/clusters/{galaxy_cluster_id}", headers=headers)
    ic(response.text)

    assert response.status_code == 200

    response_json = response.json()
    gc = response_json["GalaxyCluster"]

    assert gc["id"] == galaxy_cluster_id
    assert gc["galaxy_id"] == galaxy_id
    assert gc["type"] == add_galaxy_cluster_body3.type
    assert gc["value"] == add_galaxy_cluster_body3.value
    assert gc["tag_name"] == add_galaxy_cluster_body3.tag_name


@pytest.mark.asyncio
async def test_get_default_galaxy_cluster(db: Session, site_admin_user_token, test_default_galaxy, client) -> None:
    galaxy_cluster = test_default_galaxy["galaxy_cluster"]
    path = f"/galaxy_clusters/view/{galaxy_cluster.id}"

    headers = {"authorization": site_admin_user_token}
    response = client.get(path, headers=headers)
    ic(response.text)

    assert response.status_code == 200

    response_json = response.json()
    gc = response_json["GalaxyCluster"]
    ic(gc)
    assert gc["Org"]["id"] == 0
    assert gc["id"] == galaxy_cluster.id
    assert gc["Org"]["date_created"] == ""
    assert gc["Orgc"]["date_created"] == ""
    assert gc["Org"]["date_modified"] == ""
    assert gc["Orgc"]["date_modified"] == ""
    assert gc["Org"]["restricted_to_domain"] == []
    assert gc["Orgc"]["restricted_to_domain"] == []


@pytest.mark.asyncio
async def test_put_galaxy_cluster(db: Session, site_admin_user_token, test_galaxy, client) -> None:
    galaxy_cluster = test_galaxy["galaxy_cluster"]
    galaxy_element = test_galaxy["galaxy_element"]
    path = f"/galaxy_clusters/edit/{galaxy_cluster.id}"

    body = {
        "value": galaxy_cluster.value,
        "description": galaxy_cluster.description + " extended",
        "type": galaxy_cluster.type,
        "source": galaxy_cluster.source,
        "authors": galaxy_cluster.authors + ["first new author", "second new author"],
        "version": galaxy_cluster.version,
        "id": galaxy_cluster.id,
        "uuid": galaxy_cluster.uuid,
        "distribution": galaxy_cluster.distribution,
        "GalaxyElement": [
            {"id": galaxy_element.id, "key": "refs", "value": "http://test-one-one-one.example.com"},
            {"key": "refs", "value": "http://test-new.example.com"},
        ],
    }

    headers = {"authorization": site_admin_user_token}
    response = client.put(path, json=body, headers=headers)
    ic(response.text)

    assert response.status_code == 200

    response_json = response.json()
    gc = response_json["GalaxyCluster"]
    ic(gc)
    assert "first new author" in gc["authors"]
    assert "second new author" in gc["authors"]
    assert galaxy_cluster.description + " extended" in gc["description"]
    for ge in gc["GalaxyElement"]:
        ic(ge)
        if ge["id"] == galaxy_element.id:
            assert ge["value"] == "http://test-one-one-one.example.com"
        else:
            assert ge["value"] == "http://test-new.example.com"

    await db.execute(sa.delete(GalaxyElement).filter(GalaxyElement.galaxy_cluster_id == galaxy_cluster.id))
    await db.commit()


@pytest.mark.asyncio
async def test_get_non_existing_galaxy_cluster(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/galaxies/clusters/0", headers=headers)
    assert response.status_code == 404
    # todo: write fixture to get highest event_id, then use it here
    response = client.get("/events/500", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_existing_galaxy_details(
    db: Session, site_admin_user_token, galaxy, add_galaxy_cluster_body, add_galaxy_element, client
) -> None:
    galaxy_id = galaxy.id
    galaxy_cluster_id = add_galaxy_cluster_body.id

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/galaxies/{galaxy_id}", headers=headers)

    assert response.status_code == 200

    response_json = response.json()

    ic(response_json)
    assert response_json["Galaxy"]["id"] == galaxy_id
    assert len(response_json["GalaxyCluster"]) == 1
    assert response_json["GalaxyCluster"][0]["id"] == galaxy_cluster_id
    assert response_json["GalaxyCluster"][0]["GalaxyElement"][0]["id"] == add_galaxy_element.id
    assert response_json["GalaxyCluster"][0]["GalaxyElement"][0]["key"] == add_galaxy_element.key
    assert response_json["GalaxyCluster"][0]["GalaxyElement"][0]["value"] == add_galaxy_element.value


@pytest.mark.asyncio
async def test_get_non_existing_galaxy_details(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/galaxies/0", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_existing_galaxy(
    db: Session, site_admin_user_token, galaxy, organisation, tag, add_galaxy_cluster_body, add_galaxy_element, client
) -> None:
    galaxy_id = galaxy.id

    headers = {"authorization": site_admin_user_token}
    response = client.delete(f"/galaxies/{galaxy_id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["saved"]
    assert response_json["name"] == "Galaxy deleted"


@pytest.mark.asyncio
async def test_delete_non_existing_galaxy(site_admin_user_token, galaxy, organisation, tag, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete("/galaxies/0", headers=headers)

    assert response.status_code == 404
    response_json = response.json()
    print(response_json)
    assert response_json["detail"]["name"] == "Invalid galaxy."


@pytest.mark.asyncio
async def test_get_all_galaxies(
    db: Session, site_admin_user_token, add_galaxy_cluster_body, add_galaxy_cluster_body2, client
) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/galaxies", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)


@pytest.mark.asyncio
async def test_search_galaxies(site_admin_user_token, organisation, tag, galaxy, client) -> None:
    request_body = {"value": "test galaxy single name abcdefghijklmnopqrstuvwxyz"}

    headers = {"authorization": site_admin_user_token}
    response = client.post("/galaxies", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    for galaxy in response_json:
        assert galaxy["Galaxy"]["name"] == request_body["name"]


@pytest.mark.asyncio
async def test_export_existing_galaxy(
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
    await db.commit()
    await db.refresh(galaxy_reference)

    body = ExportGalaxyBody(Galaxy=ExportGalaxyAttributes(default=False, distribution="1"))
    request_body = body.dict()

    headers = {"authorization": site_admin_user_token}
    response = client.post(f"/galaxies/export/{galaxy_id}", json=request_body, headers=headers)
    ic(response.text)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_export_non_existing_galaxy(
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
    await db.commit()
    await db.refresh(galaxy_reference)

    body = ExportGalaxyBody(Galaxy=ExportGalaxyAttributes(default=False, distribution="1"))
    request_body = body.dict()
    headers = {"authorization": site_admin_user_token}
    response = client.post("/galaxies/export/0", json=request_body, headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_attach_cluster(site_admin_user_token, organisation, add_galaxy_cluster_body, event, client) -> None:
    galaxy_cluster_id1 = add_galaxy_cluster_body.id
    event_id = event.id

    headers = {"authorization": site_admin_user_token}

    request_body = {"Galaxy": {"target_id": galaxy_cluster_id1}}
    response = client.post(f"/galaxies/attachCluster/{event_id}/event/local:0", json=request_body, headers=headers)

    assert response.status_code == 200
    assert response.json()["success"] == "Cluster attached."


@pytest.mark.asyncio
async def test_attach_cluster_non_existing_cluster(site_admin_user_token, client) -> None:
    request_body = {"Galaxy": {"target_id": 0}}
    headers = {"authorization": site_admin_user_token}
    response = client.post("/galaxies/attachCluster/1/event/local:0", json=request_body, headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid Galaxy cluster."
