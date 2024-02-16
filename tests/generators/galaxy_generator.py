from random import Random

from mmisp.api_schemas.galaxies.export_galaxies_response import ExportGalaxyGalaxyElement, ExportGalaxyResponse
from mmisp.api_schemas.galaxies.import_galaxies_body import ImportGalaxyBody, ImportGalaxyGalaxy
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.tag import Tag

from ..environment import get_db


def generate_valid_import_galaxy_cluster_body() -> list[ImportGalaxyBody]:
    db_session = get_db()

    add_org_body = Organisation(name="test", local=True)

    db_session.add(add_org_body)
    db_session.commit()
    db_session.refresh(add_org_body)

    org_id = add_org_body.id

    add_galaxy_body = Galaxy(
        name="test galaxy",
        type="test type",
        description="test",
        version="version",
        kill_chain_order="test kill_chain_order",
    )

    db_session.add(add_galaxy_body)
    db_session.commit()
    db_session.refresh(add_galaxy_body)

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

    db_session.add(add_tag_body)
    db_session.commit()
    db_session.refresh(add_tag_body)

    tag_name = add_tag_body.name
    db_session.close()
    body = ImportGalaxyBody(
        GalaxyCluster=ExportGalaxyResponse(
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
    return response_list
