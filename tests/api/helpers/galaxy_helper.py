from mmisp.api_schemas.galaxies import (
    ExportGalaxyGalaxyElement,
    GetGalaxyClusterResponse,
    ImportGalaxyBody,
    ImportGalaxyGalaxy,
)


def get_valid_import_galaxy_body(tag_name: str, galaxy_id: int, org_id: int, galaxy_uuid: str) -> list[dict]:
    body = ImportGalaxyBody(
        GalaxyCluster=GetGalaxyClusterResponse(
            id=283,
            uuid="99b91d3f-9076-4505-82ec-76adbc9ad0de",
            collection_uuid="",
            type="test type",
            value="test",
            tag_name=tag_name,
            description="",
            galaxy_id=galaxy_id,
            source="https://github.com/mitre/cti",
            authors=["Me"],
            version="1",
            distribution=1,
            sharing_group_id=0,
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
        Galaxy=ImportGalaxyGalaxy(uuid=galaxy_uuid),
    )
    response_list = [body.model_dump()]
    return response_list


def get_invalid_import_galaxy_body(tag_name: str, galaxy_id: int, org_id: int) -> list[dict]:
    body = ImportGalaxyBody(
        GalaxyCluster=GetGalaxyClusterResponse(
            collection_uuid="",
            id=1283,
            uuid="99b91d3f-9076-4505-82ec-76adbc9ad0df",
            type="",
            value="test",
            tag_name=tag_name,
            description="",
            galaxy_id=galaxy_id,
            source="https://github.com/mitre/cti",
            authors=["Me"],
            version="1",
            distribution=1,
            sharing_group_id=0,
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
    response_list = [body.model_dump()]
    return response_list
