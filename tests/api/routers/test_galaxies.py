from random import Random

import pytest
from sqlalchemy.orm import Session

from mmisp.api_schemas.galaxies.export_galaxies_body import ExportGalaxyAttributes, ExportGalaxyBody
from mmisp.api_schemas.galaxies.export_galaxies_response import ExportGalaxyGalaxyElement
from mmisp.api_schemas.galaxies.get_galaxy_response import GetGalaxyClusterResponse
from mmisp.api_schemas.galaxies.import_galaxies_body import ImportGalaxyBody, ImportGalaxyGalaxy
from mmisp.db.models.event import Event
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement, GalaxyReference
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
            inherited=False,
            is_galaxy=True,
            is_custom_galaxy=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_name = add_tag_body.name
        body = ImportGalaxyBody(
            GalaxyCluster=GetGalaxyClusterResponse(
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
        assert response.status_code == 500
        assert response_json["detail"]["name"] == "An Internal Error Has Occurred."

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
            inherited=False,
            is_galaxy=True,
            is_custom_galaxy=False,
        )

        db.add(add_tag_body)
        db.flush()
        db.refresh(add_tag_body)

        tag_name = add_tag_body.name
        body = ImportGalaxyBody(
            GalaxyCluster=GetGalaxyClusterResponse(
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

    # def test_import_galaxy_cluster_response_format(self: "TestImportGalaxyCluster", db: Session) -> None:
    #     add_org_body = Organisation(name="test", local=True)
    #
    #     db.add(add_org_body)
    #     db.commit()
    #     db.refresh(add_org_body)
    #
    #     org_id = add_org_body.id
    #
    #     add_galaxy_body = Galaxy(
    #         name="test galaxy",
    #         type="test type",
    #         description="test",
    #         version="version",
    #         kill_chain_order="test kill_chain_order",
    #     )
    #
    #     db.add(add_galaxy_body)
    #     db.commit()
    #     db.refresh(add_galaxy_body)
    #
    #     galaxy_id = add_galaxy_body.id
    #     random = Random()
    #
    #     add_tag_body = Tag(
    #         name=str(random.randint(300001, 400000)),
    #         colour="blue",
    #         exportable=False,
    #         org_id=1,
    #         user_id=1,
    #         hide_tag=False,
    #         numerical_value=1,
    #         inherited=False,
    #         is_galaxy=True,
    #         is_custom_galaxy=False,
    #     )
    #
    #     db.add(add_tag_body)
    #     db.commit()
    #     db.refresh(add_tag_body)
    #
    #     tag_name = add_tag_body.name
    #     body = ImportGalaxyBody(
    #         GalaxyCluster=ExportGalaxyClusterResponse(
    #             collection_uuid="",
    #             type="test type",
    #             value="test",
    #             tag_name=tag_name,
    #             description="",
    #             galaxy_id=galaxy_id,
    #             source="https://github.com/mitre/cti",
    #             authors=["Me"],
    #             version="1",
    #             distribution="1",
    #             sharing_group_id="1",
    #             org_id=org_id,
    #             orgc_id=org_id,
    #             default=False,
    #             locked=False,
    #             extends_uuid="",
    #             extends_version="1",
    #             published=False,
    #             deleted="False",
    #             GalaxyElement=[ExportGalaxyGalaxyElement(key="key", value="value")],
    #         ),
    #         Galaxy=ImportGalaxyGalaxy(uuid=""),
    #     )
    #     response_list = [body.dict()]
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.post("/galaxies/import", json=response_list, headers=headers)
    #
    #     assert response.headers["Content-Type"] == "application/json"
    #
    # def test_import_galaxy_cluster_authorization(self: "TestImportGalaxyCluster", db: Session) -> None:
    #     add_org_body = Organisation(name="test", local=True)
    #
    #     db.add(add_org_body)
    #     db.commit()
    #     db.refresh(add_org_body)
    #
    #     org_id = add_org_body.id
    #
    #     add_galaxy_body = Galaxy(
    #         name="test galaxy",
    #         type="test type",
    #         description="test",
    #         version="version",
    #         kill_chain_order="test kill_chain_order",
    #     )
    #
    #     db.add(add_galaxy_body)
    #     db.commit()
    #     db.refresh(add_galaxy_body)
    #
    #     galaxy_id = add_galaxy_body.id
    #     random = Random()
    #
    #     add_tag_body = Tag(
    #         name=str(random.randint(300001, 400000)),
    #         colour="blue",
    #         exportable=False,
    #         org_id=1,
    #         user_id=1,
    #         hide_tag=False,
    #         numerical_value=1,
    #         inherited=False,
    #         is_galaxy=True,
    #         is_custom_galaxy=False,
    #     )
    #
    #     db.add(add_tag_body)
    #     db.commit()
    #     db.refresh(add_tag_body)
    #
    #     tag_name = add_tag_body.name
    #     body = ImportGalaxyBody(
    #         GalaxyCluster=ExportGalaxyClusterResponse(
    #             collection_uuid="",
    #             type="test type",
    #             value="test",
    #             tag_name=tag_name,
    #             description="",
    #             galaxy_id=galaxy_id,
    #             source="https://github.com/mitre/cti",
    #             authors=["Me"],
    #             version="1",
    #             distribution="1",
    #             sharing_group_id="1",
    #             org_id=org_id,
    #             orgc_id=org_id,
    #             default=False,
    #             locked=False,
    #             extends_uuid="",
    #             extends_version="1",
    #             published=False,
    #             deleted="False",
    #             GalaxyElement=[ExportGalaxyGalaxyElement(key="key", value="value")],
    #         ),
    #         Galaxy=ImportGalaxyGalaxy(uuid=""),
    #     )
    #     response_list = [body.dict()]
    #     headers = {"authorization": ""}
    #     response = client.post("/galaxies/import", json=response_list, headers=headers)
    #     assert response.status_code == 401


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
            inherited=False,
            is_galaxy=True,
            is_custom_galaxy=False,
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

    # def test_get_galaxy_details_response_format(self: "TestGetGalaxyDetails", db: Session) -> None:
    #     random = Random()
    #
    #     add_tag_body = Tag(
    #         name=str(random.randint(900001, 1000000)),
    #         colour="blue",
    #         exportable=False,
    #         org_id=1,
    #         user_id=1,
    #         hide_tag=False,
    #         numerical_value=1,
    #         inherited=False,
    #         is_galaxy=True,
    #         is_custom_galaxy=False,
    #     )
    #
    #     db.add(add_tag_body)
    #     db.commit()
    #     db.refresh(add_tag_body)
    #
    #     tag_name = add_tag_body.name
    #
    #     add_galaxy_body = Galaxy(
    #         name="test galaxy",
    #         type="test type",
    #         description="test",
    #         version="version",
    #         kill_chain_order="test kill_chain_order",
    #     )
    #
    #     db.add(add_galaxy_body)
    #     db.commit()
    #     db.refresh(add_galaxy_body)
    #
    #     galaxy_id = add_galaxy_body.id
    #
    #     add_galaxy_cluster_body = GalaxyCluster(
    #         type="test", value="test", tag_name=tag_name, description="", galaxy_id=galaxy_id, authors="Me"
    #     )
    #
    #     db.add(add_galaxy_cluster_body)
    #     db.commit()
    #     db.refresh(add_galaxy_cluster_body)
    #
    #     galaxy_cluster_id = add_galaxy_cluster_body.id
    #
    #     add_galaxy_element = GalaxyElement(galaxy_cluster_id=galaxy_cluster_id, key="refs", value="http://github.com")
    #
    #     db.add(add_galaxy_element)
    #     db.commit()
    #     db.refresh(add_galaxy_element)
    #
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.get(f"/galaxies/{galaxy_id}", headers=headers)
    #
    #     assert response.headers["Content-Type"] == "application/json"


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
            inherited=False,
            is_galaxy=True,
            is_custom_galaxy=False,
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

    # def test_delete_galaxy_response_format(self: "TestDeleteGalaxy", db: Session) -> None:
    #     random = Random()
    #
    #     add_tag_body = Tag(
    #         name=str(random.randint(800001, 900000)),
    #         colour="blue",
    #         exportable=False,
    #         org_id=1,
    #         user_id=1,
    #         hide_tag=False,
    #         numerical_value=1,
    #         inherited=False,
    #         is_galaxy=True,
    #         is_custom_galaxy=False,
    #     )
    #
    #     db.add(add_tag_body)
    #     db.commit()
    #     db.refresh(add_tag_body)
    #
    #     tag_name = add_tag_body.name
    #
    #     add_galaxy_body = Galaxy(
    #         name="test galaxy",
    #         type="test type",
    #         description="test",
    #         version="version",
    #         kill_chain_order="test kill_chain_order",
    #     )
    #
    #     db.add(add_galaxy_body)
    #     db.commit()
    #     db.refresh(add_galaxy_body)
    #
    #     galaxy_id = add_galaxy_body.id
    #
    #     add_galaxy_cluster_body = GalaxyCluster(
    #         type="test", value="test", tag_name=tag_name, description="", galaxy_id=galaxy_id, authors="Me"
    #     )
    #
    #     db.add(add_galaxy_cluster_body)
    #     db.commit()
    #     db.refresh(add_galaxy_cluster_body)
    #
    #     galaxy_cluster_id = add_galaxy_cluster_body.id
    #
    #     add_galaxy_element = GalaxyElement(galaxy_cluster_id=galaxy_cluster_id, key="refs", value="http://github.com")
    #
    #     db.add(add_galaxy_element)
    #     db.commit()
    #     db.refresh(add_galaxy_element)
    #     headers = {"authorization": environment.site_admin_user_token}
    #     response = client.delete(f"/galaxies/{galaxy_id}", headers=headers)
    #
    #     assert response.headers["Content-Type"] == "application/json"
    #
    # def test_delete_galaxy_authorization(self: "TestDeleteGalaxy") -> None:
    #     headers = {"authorization": ""}
    #     response = client.delete("/galaxies/1", headers=headers)
    #
    #     assert response.status_code == 401


class TestGetAllGalaxies:
    def test_get_all_galaxies(self: "TestGetAllGalaxies", db: Session) -> None:
        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(1000001, 1100000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            inherited=False,
            is_galaxy=True,
            is_custom_galaxy=False,
        )

        db.add(add_tag_body)
        db.commit()
        db.refresh(add_tag_body)

        tag_name = add_tag_body.name

        add_galaxy_body1 = Galaxy(
            name="test galaxy1",
            type="test type",
            description="test",
            version="version",
            kill_chain_order="test kill_chain_order",
        )

        db.add(add_galaxy_body1)
        db.commit()
        db.refresh(add_galaxy_body1)

        add_galaxy_body2 = Galaxy(
            name="test galaxy2",
            type="test type",
            description="test",
            version="version",
            kill_chain_order="test kill_chain_order",
        )

        db.add(add_galaxy_body2)
        db.commit()
        db.refresh(add_galaxy_body2)

        add_galaxy_cluster_body1 = GalaxyCluster(
            type="test", value="test", tag_name=tag_name, description="", galaxy_id=add_galaxy_body1.id, authors="Me"
        )

        add_galaxy_cluster_body2 = GalaxyCluster(
            type="test", value="test", tag_name=tag_name, description="", galaxy_id=add_galaxy_body2.id, authors="Me"
        )

        db.add(add_galaxy_cluster_body1)
        db.commit()
        db.refresh(add_galaxy_cluster_body1)

        db.add(add_galaxy_cluster_body2)
        db.commit()
        db.refresh(add_galaxy_cluster_body2)

        response = client.get("/galaxies")

        assert response.status_code == 200
        response_json = response.json()
        assert isinstance(response_json, list)


class TestExportGalaxy:
    def test_export_existing_galaxy(self: "TestExportGalaxy", db: Session) -> None:
        add_org_body = Organisation(name="test", local=True, type="test", created_by=1)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(1100001, 1200000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            inherited=False,
            is_galaxy=True,
            is_custom_galaxy=False,
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

        add_galaxy_cluster_body1 = GalaxyCluster(
            type="test type",
            value="test",
            tag_name=tag_name,
            description="",
            galaxy_id=galaxy_id,
            authors="Me",
            default=False,
            distribution=1,
            org_id=org_id,
            orgc_id=org_id,
        )

        db.add(add_galaxy_cluster_body1)
        db.commit()
        db.refresh(add_galaxy_cluster_body1)

        galaxy_cluster_id1 = add_galaxy_cluster_body1.id

        add_galaxy_cluster_body = GalaxyCluster(
            type="test",
            value="test",
            tag_name=tag_name,
            description="",
            galaxy_id=galaxy_id,
            authors="Me",
            default=False,
            distribution=1,
            org_id=org_id,
            orgc_id=org_id,
        )

        db.add(add_galaxy_cluster_body)
        db.commit()
        db.refresh(add_galaxy_cluster_body)

        galaxy_cluster_id = add_galaxy_cluster_body.id

        add_galaxy_element = GalaxyElement(galaxy_cluster_id=galaxy_cluster_id, key="refs", value="http://github.com")

        db.add(add_galaxy_element)
        db.commit()
        db.refresh(add_galaxy_element)

        galaxy_reference = GalaxyReference(
            galaxy_cluster_id=galaxy_cluster_id1,
            referenced_galaxy_cluster_id=add_galaxy_cluster_body1.id,
            referenced_galaxy_cluster_uuid=add_galaxy_cluster_body1.uuid,
            referenced_galaxy_cluster_type=add_galaxy_cluster_body1.type,
            referenced_galaxy_cluster_value=add_galaxy_cluster_body1.value,
        )

        db.add(galaxy_reference)
        db.commit()
        db.refresh(galaxy_reference)

        body = ExportGalaxyBody(Galaxy=ExportGalaxyAttributes(default=False, distribution="1"))
        body_dict = body.dict()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/galaxies/export/{galaxy_id}", json=body_dict, headers=headers)

        assert response.status_code == 200

    def test_export_non_existing_galaxy(self: "TestExportGalaxy", db: Session) -> None:
        add_org_body = Organisation(name="test", local=True, type="test", created_by=1)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(1100001, 1200000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            inherited=False,
            is_galaxy=True,
            is_custom_galaxy=False,
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

        add_galaxy_cluster_body1 = GalaxyCluster(
            type="test type",
            value="test",
            tag_name=tag_name,
            description="",
            galaxy_id=galaxy_id,
            authors="Me",
            default=False,
            distribution=1,
            org_id=org_id,
            orgc_id=org_id,
        )

        db.add(add_galaxy_cluster_body1)
        db.commit()
        db.refresh(add_galaxy_cluster_body1)

        galaxy_cluster_id1 = add_galaxy_cluster_body1.id

        add_galaxy_cluster_body = GalaxyCluster(
            type="test",
            value="test",
            tag_name=tag_name,
            description="",
            galaxy_id=galaxy_id,
            authors="Me",
            default=False,
            distribution=1,
            org_id=org_id,
            orgc_id=org_id,
        )

        db.add(add_galaxy_cluster_body)
        db.commit()
        db.refresh(add_galaxy_cluster_body)

        galaxy_cluster_id = add_galaxy_cluster_body.id

        add_galaxy_element = GalaxyElement(galaxy_cluster_id=galaxy_cluster_id, key="refs", value="http://github.com")

        db.add(add_galaxy_element)
        db.commit()
        db.refresh(add_galaxy_element)

        galaxy_reference = GalaxyReference(
            galaxy_cluster_id=galaxy_cluster_id1,
            referenced_galaxy_cluster_id=add_galaxy_cluster_body1.id,
            referenced_galaxy_cluster_uuid=add_galaxy_cluster_body1.uuid,
            referenced_galaxy_cluster_type=add_galaxy_cluster_body1.type,
            referenced_galaxy_cluster_value=add_galaxy_cluster_body1.value,
        )

        db.add(galaxy_reference)
        db.commit()
        db.refresh(galaxy_reference)

        body = ExportGalaxyBody(Galaxy=ExportGalaxyAttributes(default=False, distribution="1"))
        body_dict = body.dict()
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/galaxies/export/0", json=body_dict, headers=headers)

        assert response.status_code == 404


class TestAttachCluster:
    def test_attach_cluster(self: "TestAttachCluster", db: Session) -> None:
        add_org_body = Organisation(name="test", local=True, type="test", created_by=1)

        db.add(add_org_body)
        db.commit()
        db.refresh(add_org_body)

        org_id = add_org_body.id

        random = Random()

        add_tag_body = Tag(
            name=str(random.randint(1100001, 1200000)),
            colour="blue",
            exportable=False,
            org_id=1,
            user_id=1,
            hide_tag=False,
            numerical_value=1,
            inherited=False,
            is_galaxy=True,
            is_custom_galaxy=False,
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

        add_galaxy_cluster_body1 = GalaxyCluster(
            type="test type",
            value="test",
            tag_name=tag_name,
            description="",
            galaxy_id=galaxy_id,
            authors="Me",
            default=False,
            distribution=1,
            org_id=org_id,
            orgc_id=org_id,
        )

        db.add(add_galaxy_cluster_body1)
        db.commit()
        db.refresh(add_galaxy_cluster_body1)

        galaxy_cluster_id1 = add_galaxy_cluster_body1.id

        add_event_body = Event(
            org_id=org_id,
            orgc_id=org_id,
            info="test event",
            date="2024-02-13",
            analysis="test analysis",
            event_creator_email="test@mail.de",
        )

        db.add(add_event_body)
        db.commit()
        db.refresh(add_event_body)

        event_id = add_event_body.id

        headers = {"authorization": environment.site_admin_user_token}

        body_dict = {"Galaxy": {"target_id": galaxy_cluster_id1}}
        response = client.post(f"/galaxies/attachCluster/{event_id}/event/local:0", json=body_dict, headers=headers)

        assert response.status_code == 200
        assert response.json()["success"] == "Cluster attached."

    def test_attach_cluster_non_existing_cluster(self: "TestAttachCluster") -> None:
        body_dict = {"Galaxy": {"target_id": 0}}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/galaxies/attachCluster/1/event/local:0", json=body_dict, headers=headers)

        assert response.status_code == 404
        assert response.json()["detail"] == "Invalid Galaxy cluster."
