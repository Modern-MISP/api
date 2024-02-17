from random import Random

import pytest
from sqlalchemy.orm import Session

from mmisp.api_schemas.galaxies.export_galaxies_response import ExportGalaxyClusterResponse, ExportGalaxyGalaxyElement
from mmisp.api_schemas.galaxies.import_galaxies_body import ImportGalaxyBody, ImportGalaxyGalaxy
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.tag import Tag

from ...environment import client, environment, get_db


@pytest.fixture(scope="function")
def db() -> Session:
    db_session = get_db()

    yield db_session

    db_session.close()


class TestImportGalaxyCluster:
    def test_import_galaxy_cluster_valid_data(self: "TestImportGalaxyCluster", db: Session) -> None:
        add_org_body = Organisation(name="test", local=True)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_galaxy_body = Galaxy(
            name="test galaxy",
            type="test type",
            description="test",
            version="version",
            kill_chain_order="test kill_chain_order",
        )

        db.add(add_galaxy_body)
        db.commit()
        db.refresh(add_galaxy_body)

        galaxy_id = add_galaxy_body.id
        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(300001, 400000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            is_galaxy=True,
            is_custom_galaxy=False,
            attribute_count=1,
            count=1,
            favourite=False,
            local_only=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_name = add_tag_body.name
        body = ImportGalaxyBody(
            GalaxyCluster=ExportGalaxyClusterResponse(
                collection_uuid="",
                type="test type",
                value="test",
                tag_name=tag_name,
                description="",
                galaxy_id=galaxy_id,
                source="https://github.com/mitre/cti",
                authors=["Me"],
                version="1",
                distribution="1",
                sharing_group_id="1",
                org_id=org_id,
                orgc_id=org_id,
                default=False,
                locked=False,
                extends_uuid="",
                extends_version="1",
                published=False,
                deleted="False",
                GalaxyElement=[ExportGalaxyGalaxyElement(key="key", value="value")],
            ),
            Galaxy=ImportGalaxyGalaxy(uuid=add_galaxy_body.uuid),
        )
        response_list = [body.dict()]
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/galaxies/import", json=response_list, headers=headers)
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["saved"] is True
        assert response_json["success"] is True
        assert response_json["name"] == "Galaxy clusters imported. 1 imported, 0 ignored, 0 failed."

    def test_import_galaxy_cluster_invalid_data(self: "TestImportGalaxyCluster", db: Session) -> None:
        add_org_body = Organisation(name="test", local=True)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_galaxy_body = Galaxy(
            name="test galaxy",
            type="test type",
            description="test",
            version="version",
            kill_chain_order="test kill_chain_order",
        )

        db.add(add_galaxy_body)
        db.flush()
        db.refresh(add_galaxy_body)

        galaxy_id = add_galaxy_body.id
        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(300001, 400000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            is_galaxy=True,
            is_custom_galaxy=False,
            attribute_count=1,
            count=1,
            favourite=False,
            local_only=False,
        )

        db.add(add_tag_body)
        db.flush()
        db.refresh(add_tag_body)

        tag_name = add_tag_body.name
        body = ImportGalaxyBody(
            GalaxyCluster=ExportGalaxyClusterResponse(
                collection_uuid="",
                type="",
                value="test",
                tag_name=tag_name,
                description="",
                galaxy_id=galaxy_id,
                source="https://github.com/mitre/cti",
                authors=["Me"],
                version="1",
                distribution="1",
                sharing_group_id="1",
                org_id=org_id,
                orgc_id=org_id,
                default=False,
                locked=False,
                extends_uuid="",
                extends_version="1",
                published=False,
                deleted="False",
                GalaxyElement=[ExportGalaxyGalaxyElement(key="key", value="value")],
            ),
            Galaxy=ImportGalaxyGalaxy(uuid=""),
        )
        response_list = [body.dict()]
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/galaxies/import", json=response_list, headers=headers)

        assert response.status_code == 403

    def test_import_galaxy_cluster_response_format(self: "TestImportGalaxyCluster", db: Session) -> None:
        add_org_body = Organisation(name="test", local=True)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_galaxy_body = Galaxy(
            name="test galaxy",
            type="test type",
            description="test",
            version="version",
            kill_chain_order="test kill_chain_order",
        )

        db.add(add_galaxy_body)
        db.commit()
        db.refresh(add_galaxy_body)

        galaxy_id = add_galaxy_body.id
        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(300001, 400000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            is_galaxy=True,
            is_custom_galaxy=False,
            attribute_count=1,
            count=1,
            favourite=False,
            local_only=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_name = add_tag_body.name
        body = ImportGalaxyBody(
            GalaxyCluster=ExportGalaxyClusterResponse(
                collection_uuid="",
                type="test type",
                value="test",
                tag_name=tag_name,
                description="",
                galaxy_id=galaxy_id,
                source="https://github.com/mitre/cti",
                authors=["Me"],
                version="1",
                distribution="1",
                sharing_group_id="1",
                org_id=org_id,
                orgc_id=org_id,
                default=False,
                locked=False,
                extends_uuid="",
                extends_version="1",
                published=False,
                deleted="False",
                GalaxyElement=[ExportGalaxyGalaxyElement(key="key", value="value")],
            ),
            Galaxy=ImportGalaxyGalaxy(uuid=""),
        )
        response_list = [body.dict()]
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/galaxies/import", json=response_list, headers=headers)

        assert response.headers["Content-Type"] == "application/json"

    def test_import_galaxy_cluster_authorization(self: "TestImportGalaxyCluster", db: Session) -> None:
        add_org_body = Organisation(name="test", local=True)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        add_galaxy_body = Galaxy(
            name="test galaxy",
            type="test type",
            description="test",
            version="version",
            kill_chain_order="test kill_chain_order",
        )

        db.add(add_galaxy_body)
        db.commit()
        db.refresh(add_galaxy_body)

        galaxy_id = add_galaxy_body.id
        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(300001, 400000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            is_galaxy=True,
            is_custom_galaxy=False,
            attribute_count=1,
            count=1,
            favourite=False,
            local_only=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_name = add_tag_body.name
        body = ImportGalaxyBody(
            GalaxyCluster=ExportGalaxyClusterResponse(
                collection_uuid="",
                type="test type",
                value="test",
                tag_name=tag_name,
                description="",
                galaxy_id=galaxy_id,
                source="https://github.com/mitre/cti",
                authors=["Me"],
                version="1",
                distribution="1",
                sharing_group_id="1",
                org_id=org_id,
                orgc_id=org_id,
                default=False,
                locked=False,
                extends_uuid="",
                extends_version="1",
                published=False,
                deleted="False",
                GalaxyElement=[ExportGalaxyGalaxyElement(key="key", value="value")],
            ),
            Galaxy=ImportGalaxyGalaxy(uuid=""),
        )
        response_list = [body.dict()]
        headers = {"authorization": ""}
        response = client.post("/galaxies/import", json=response_list, headers=headers)
        assert response.status_code == 401


class TestGetGalaxyDetails:
    def test_get_existing_galaxy_details(self: "TestGetGalaxyDetails", db: Session) -> None:
        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(600001, 700000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            is_galaxy=True,
            is_custom_galaxy=False,
            attribute_count=1,
            count=1,
            favourite=False,
            local_only=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_name = add_tag_body.name

        add_galaxy_body = Galaxy(
            name="test galaxy",
            type="test type",
            description="test",
            version="version",
            kill_chain_order="test kill_chain_order",
        )

        db.add(add_galaxy_body)
        db.commit()
        db.refresh(add_galaxy_body)

        galaxy_id = add_galaxy_body.id

        add_galaxy_cluster_body = GalaxyCluster(
            type="test", value="test", tag_name=tag_name, description="", galaxy_id=galaxy_id, authors="Me"
        )

        db.add(add_galaxy_cluster_body)
        db.commit()
        db.refresh(add_galaxy_cluster_body)

        galaxy_cluster_id = add_galaxy_cluster_body.id

        add_galaxy_element = GalaxyElement(galaxy_cluster_id=galaxy_cluster_id, key="refs", value="http://github.com")

        db.add(add_galaxy_element)
        db.commit()
        db.refresh(add_galaxy_element)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/galaxies/{galaxy_id}", headers=headers)

        assert response.status_code == 200

        response_json = response.json()

        assert response_json["Galaxy"]["id"] == str(galaxy_id)
        assert response_json["GalaxyCluster"][0]["id"] == str(galaxy_cluster_id)
        assert response_json["GalaxyCluster"][0]["GalaxyElement"][0]["id"] == str(add_galaxy_element.id)
        assert response_json["GalaxyCluster"][0]["GalaxyElement"][0]["key"] == add_galaxy_element.key
        assert response_json["GalaxyCluster"][0]["GalaxyElement"][0]["value"] == add_galaxy_element.value

    def test_get_non_existing_galaxy_details(self: "TestGetGalaxyDetails") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/galaxies/0", headers=headers)

        assert response.status_code == 404

    def test_get_galaxy_details_response_format(self: "TestGetGalaxyDetails", db: Session) -> None:
        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(900001, 1000000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            is_galaxy=True,
            is_custom_galaxy=False,
            attribute_count=1,
            count=1,
            favourite=False,
            local_only=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_name = add_tag_body.name

        add_galaxy_body = Galaxy(
            name="test galaxy",
            type="test type",
            description="test",
            version="version",
            kill_chain_order="test kill_chain_order",
        )

        db.add(add_galaxy_body)
        db.commit()
        db.refresh(add_galaxy_body)

        galaxy_id = add_galaxy_body.id

        add_galaxy_cluster_body = GalaxyCluster(
            type="test", value="test", tag_name=tag_name, description="", galaxy_id=galaxy_id, authors="Me"
        )

        db.add(add_galaxy_cluster_body)
        db.commit()
        db.refresh(add_galaxy_cluster_body)

        galaxy_cluster_id = add_galaxy_cluster_body.id

        add_galaxy_element = GalaxyElement(galaxy_cluster_id=galaxy_cluster_id, key="refs", value="http://github.com")

        db.add(add_galaxy_element)
        db.commit()
        db.refresh(add_galaxy_element)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/galaxies/{galaxy_id}", headers=headers)

        assert response.headers["Content-Type"] == "application/json"


class TestDeleteGalaxy:
    def test_delete_existing_galaxy(self: "TestDeleteGalaxy", db: Session) -> None:
        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(700001, 800000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            is_galaxy=True,
            is_custom_galaxy=False,
            attribute_count=1,
            count=1,
            favourite=False,
            local_only=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_name = add_tag_body.name

        add_galaxy_body = Galaxy(
            name="test galaxy",
            type="test type",
            description="test",
            version="version",
            kill_chain_order="test kill_chain_order",
        )

        db.add(add_galaxy_body)
        db.commit()
        db.refresh(add_galaxy_body)

        galaxy_id = add_galaxy_body.id

        add_galaxy_cluster_body = GalaxyCluster(
            type="test", value="test", tag_name=tag_name, description="", galaxy_id=galaxy_id, authors="Me"
        )

        db.add(add_galaxy_cluster_body)
        db.commit()
        db.refresh(add_galaxy_cluster_body)

        galaxy_cluster_id = add_galaxy_cluster_body.id

        add_galaxy_element = GalaxyElement(galaxy_cluster_id=galaxy_cluster_id, key="refs", value="http://github.com")

        db.add(add_galaxy_element)
        db.commit()
        db.refresh(add_galaxy_element)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/galaxies/{galaxy_id}", headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["saved"] is True
        assert response_json["name"] == "Galaxy deleted"

    def test_delete_non_existing_galaxy(self: "TestDeleteGalaxy") -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete("/galaxies/0", headers=headers)

        assert response.status_code == 404
        response_json = response.json()
        print(response_json)
        assert response_json["detail"]["name"] == "Invalid galaxy."

    def test_delete_galaxy_response_format(self: "TestDeleteGalaxy", db: Session) -> None:
        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(800001, 900000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            is_galaxy=True,
            is_custom_galaxy=False,
            attribute_count=1,
            count=1,
            favourite=False,
            local_only=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_name = add_tag_body.name

        add_galaxy_body = Galaxy(
            name="test galaxy",
            type="test type",
            description="test",
            version="version",
            kill_chain_order="test kill_chain_order",
        )

        db.add(add_galaxy_body)
        db.commit()
        db.refresh(add_galaxy_body)

        galaxy_id = add_galaxy_body.id

        add_galaxy_cluster_body = GalaxyCluster(
            type="test", value="test", tag_name=tag_name, description="", galaxy_id=galaxy_id, authors="Me"
        )

        db.add(add_galaxy_cluster_body)
        db.commit()
        db.refresh(add_galaxy_cluster_body)

        galaxy_cluster_id = add_galaxy_cluster_body.id

        add_galaxy_element = GalaxyElement(galaxy_cluster_id=galaxy_cluster_id, key="refs", value="http://github.com")

        db.add(add_galaxy_element)
        db.commit()
        db.refresh(add_galaxy_element)
        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete(f"/galaxies/{galaxy_id}", headers=headers)

        assert response.headers["Content-Type"] == "application/json"

    def test_delete_galaxy_authorization(self: "TestDeleteGalaxy") -> None:
        headers = {"authorization": ""}
        response = client.delete("/galaxies/1", headers=headers)

        assert response.status_code == 401
