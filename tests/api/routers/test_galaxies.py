from sqlalchemy.orm import Session

from mmisp.api_schemas.galaxies.export_galaxies_body import ExportGalaxyAttributes, ExportGalaxyBody
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement, GalaxyReference

from ...environment import client, environment
from ...generators.model_generators.event_generator import generate_event
from ...generators.model_generators.galaxy_generator import generate_galaxy
from ...generators.model_generators.organisation_generator import generate_organisation
from ...generators.model_generators.tag_generator import generate_tag
from ..helpers.galaxy_helper import get_invalid_import_galaxy_body, get_valid_import_galaxy_body


class TestImportGalaxyCluster:
    @staticmethod
    def test_import_galaxy_cluster_valid_data(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        galaxy = generate_galaxy()

        db.add(galaxy)
        db.commit()
        db.refresh(galaxy)

        galaxy_id = galaxy.id

        tag = generate_tag()
        setattr(tag, "user_id", 1)
        setattr(tag, "org_id", 1)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        tag_name = tag.name

        request_body = get_valid_import_galaxy_body(tag_name, galaxy_id, org_id, galaxy.uuid)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/galaxies/import", json=request_body, headers=headers)
        response_json = response.json()
        print(response_json)
        assert response.status_code == 200
        assert response_json["name"] == "Galaxy clusters imported. 1 imported, 0 ignored, 0 failed."

    @staticmethod
    def test_import_galaxy_cluster_invalid_data(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        galaxy = generate_galaxy()

        db.add(galaxy)
        db.commit()
        db.refresh(galaxy)

        galaxy_id = galaxy.id

        tag = generate_tag()
        setattr(tag, "user_id", 1)
        setattr(tag, "org_id", 1)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        tag_name = tag.name

        request_body = get_invalid_import_galaxy_body(tag_name, galaxy_id, org_id)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/galaxies/import", json=request_body, headers=headers)

        assert response.status_code == 403


class TestGetGalaxyDetails:
    @staticmethod
    def test_get_existing_galaxy_details(db: Session) -> None:
        tag = generate_tag()
        setattr(tag, "user_id", 1)
        setattr(tag, "org_id", 1)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        tag_name = tag.name

        galaxy = generate_galaxy()

        db.add(galaxy)
        db.commit()
        db.refresh(galaxy)

        galaxy_id = galaxy.id

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

    @staticmethod
    def test_get_non_existing_galaxy_details() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/galaxies/0", headers=headers)

        assert response.status_code == 404


class TestDeleteGalaxy:
    @staticmethod
    def test_delete_existing_galaxy(db: Session) -> None:
        tag = generate_tag()
        setattr(tag, "user_id", 1)
        setattr(tag, "org_id", 1)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        tag_name = tag.name

        galaxy = generate_galaxy()

        db.add(galaxy)
        db.commit()
        db.refresh(galaxy)

        galaxy_id = galaxy.id

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

    @staticmethod
    def test_delete_non_existing_galaxy() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.delete("/galaxies/0", headers=headers)

        assert response.status_code == 404
        response_json = response.json()
        print(response_json)
        assert response_json["detail"]["name"] == "Invalid galaxy."


class TestGetAllGalaxies:
    @staticmethod
    def test_get_all_galaxies(db: Session) -> None:
        tag = generate_tag()
        setattr(tag, "user_id", 1)
        setattr(tag, "org_id", 1)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        tag_name = tag.name
        print(tag.name)

        galaxy1 = generate_galaxy()

        db.add(galaxy1)
        db.commit()
        db.refresh(galaxy1)

        galaxy1_id = galaxy1.id

        galaxy2 = generate_galaxy()

        db.add(galaxy2)
        db.commit()
        db.refresh(galaxy2)

        galaxy2_id = galaxy2.id

        add_galaxy_cluster_body1 = GalaxyCluster(
            type="test", value="test", tag_name=tag_name, description="", galaxy_id=galaxy1_id, authors="Me"
        )
        print(add_galaxy_cluster_body1.tag_name)

        add_galaxy_cluster_body2 = GalaxyCluster(
            type="test", value="test", tag_name=tag_name, description="", galaxy_id=galaxy2_id, authors="Me"
        )
        print(add_galaxy_cluster_body2.tag_name)

        db.add(add_galaxy_cluster_body1)
        db.commit()
        db.refresh(add_galaxy_cluster_body1)

        db.add(add_galaxy_cluster_body2)
        db.commit()
        db.refresh(add_galaxy_cluster_body2)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/galaxies", headers=headers)

        assert response.status_code == 200
        response_json = response.json()
        assert isinstance(response_json, list)


class TestExportGalaxy:
    @staticmethod
    def test_export_existing_galaxy(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        tag = generate_tag()
        setattr(tag, "user_id", 1)
        setattr(tag, "org_id", 1)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        tag_name = tag.name

        galaxy = generate_galaxy()

        db.add(galaxy)
        db.commit()
        db.refresh(galaxy)

        galaxy_id = galaxy.id

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
        request_body = body.dict()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(f"/galaxies/export/{galaxy_id}", json=request_body, headers=headers)

        assert response.status_code == 200

    @staticmethod
    def test_export_non_existing_galaxy(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        tag = generate_tag()
        setattr(tag, "user_id", 1)
        setattr(tag, "org_id", 1)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        tag_name = tag.name

        galaxy = generate_galaxy()

        db.add(galaxy)
        db.commit()
        db.refresh(galaxy)

        galaxy_id = galaxy.id

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
        request_body = body.dict()
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/galaxies/export/0", json=request_body, headers=headers)

        assert response.status_code == 404


class TestAttachCluster:
    @staticmethod
    def test_attach_cluster(db: Session) -> None:
        organisation = generate_organisation()

        db.add(organisation)
        db.commit()
        db.refresh(organisation)

        org_id = organisation.id

        tag = generate_tag()
        setattr(tag, "user_id", 1)
        setattr(tag, "org_id", 1)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        tag_name = tag.name

        galaxy = generate_galaxy()

        db.add(galaxy)
        db.commit()
        db.refresh(galaxy)

        galaxy_id = galaxy.id

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

        event = generate_event()

        db.add(event)
        db.commit()
        db.refresh(event)

        event_id = event.id

        setattr(event, "org_id", org_id)
        setattr(event, "orgc_id", org_id)

        headers = {"authorization": environment.site_admin_user_token}

        request_body = {"Galaxy": {"target_id": galaxy_cluster_id1}}
        response = client.post(f"/galaxies/attachCluster/{event_id}/event/local:0", json=request_body, headers=headers)

        assert response.status_code == 200
        assert response.json()["success"] == "Cluster attached."

    @staticmethod
    def test_attach_cluster_non_existing_cluster() -> None:
        request_body = {"Galaxy": {"target_id": 0}}
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/galaxies/attachCluster/1/event/local:0", json=request_body, headers=headers)

        assert response.status_code == 404
        assert response.json()["detail"] == "Invalid Galaxy cluster."
