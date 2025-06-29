import time
from collections.abc import Sequence
from enum import StrEnum
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from starlette import status
from starlette.requests import Request

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.events import (
    AddEditGetEventGalaxyClusterRelation,
    AddEditGetEventGalaxyClusterRelationTag,
)
from mmisp.api_schemas.galaxies import (
    AttachClusterGalaxyBody,
    AttachClusterGalaxyResponse,
    DeleteForceUpdateImportGalaxyResponse,
    ExportGalaxyBody,
    ExportGalaxyClusterResponse,
    ExportGalaxyGalaxyElement,
    ImportGalaxyBody,
    RestSearchGalaxyBody,
)
from mmisp.api_schemas.galaxy_clusters import (
    AddGalaxyClusterRequest,
    GalaxyClusterResponse,
    GalaxyClusterSearchBody,
    GalaxyClusterSearchResponse,
    GetGalaxyClusterResponse,
    IndexGalaxyCluster,
    PutGalaxyClusterRequest,
    SearchGalaxyClusterGalaxyClusters,
    SearchGalaxyClusterGalaxyClustersDetails,
)
from mmisp.api_schemas.galaxy_common import ShortCommonGalaxy, ShortCommonGalaxyCluster
from mmisp.api_schemas.organisations import GetOrganisationElement
from mmisp.db.database import Session, get_db
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.event import Event, EventTag
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement, GalaxyReference
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.tag import Tag
from mmisp.db.models.user import User
from mmisp.lib.fallbacks import GENERIC_MISP_ORGANISATION
from mmisp.lib.galaxies import galaxy_tag_name, parse_galaxy_authors
from mmisp.lib.galaxy_clusters import update_galaxy_cluster_elements
from mmisp.lib.logger import alog, log
from mmisp.lib.tags import get_or_create_instance_tag
from mmisp.util.uuid import uuid

router = APIRouter(tags=["galaxy_clusters"])


@router.post(
    "/galaxies/import",
    status_code=status.HTTP_200_OK,
    summary="Add new galaxy cluster",
)
@alog
async def import_galaxy_cluster(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.GALAXY_EDITOR]))],
    db: Annotated[Session, Depends(get_db)],
    body: list[ImportGalaxyBody],
    request: Request,
) -> DeleteForceUpdateImportGalaxyResponse:
    """Add a new galaxy cluster to an existing galaxy.

    args:

    - the user's authentification status

    - the current database

    - the request body

    - the request

    returns:

    - the new galaxy cluster
    """
    return await _import_galaxy_cluster(db, body, request)


@router.get(
    "/galaxies/clusters/{clusterID}",
    status_code=status.HTTP_200_OK,
    summary="Gets information from a galaxy cluster",
)
@alog
async def get_galaxy_cluster(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    cluster_id: Annotated[int, Path(alias="clusterID")],
) -> GalaxyClusterResponse:
    """Returns information from a galaxy cluster selected by its id.

    args:

    - the user's authentification status

    - the current database

    - the galaxy id

    returns:

    - the information of the galaxy cluster
    """
    return await _get_galaxy_cluster(db, await _load_galaxy_cluster(db, cluster_id))


@router.post(
    "/galaxies/export/{galaxyId}",
    status_code=status.HTTP_200_OK,
    summary="Export galaxy cluster",
)
@alog
async def export_galaxy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[str, Path(alias="galaxyId")],
    body: ExportGalaxyBody,
) -> list[ExportGalaxyClusterResponse]:
    """Export galaxy cluster.

    args:

    - the user's authentification status

    - the current database

    - the galaxy id

    - the request body

    returns:

    - the exported galaxy cluster
    """
    return await _export_galaxy(db, galaxy_id, body)


class AttachTargetTypes(StrEnum):
    EVENT = "event"
    ATTRIBUTE = "attribute"
    TAG_COLLECTION = "tag_collection"


@router.post(
    "/galaxies/attachCluster/{attachTargetId}/{attachTargetType}/local:{local}",
    status_code=status.HTTP_200_OK,
    summary="Attach Cluster to Galaxy.",
)
@alog
async def galaxies_attachCluster(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    attach_target_id: Annotated[str, Path(alias="attachTargetId")],
    attach_target_type: Annotated[AttachTargetTypes, Path(alias="attachTargetType")],
    body: AttachClusterGalaxyBody,
    local: bool,
) -> AttachClusterGalaxyResponse:
    """Attach a Galaxy Cluster to given Galaxy.

    args:
      auth: the user's authentification status
      db: the current database
      attach_target_id: the id of the attach target
      attach_target_type: the type of the attach target
      body: the request body
      local: local

    returns:
      the attached galaxy cluster and the attach target
    """
    return await _attach_cluster_to_galaxy(db, auth.user, attach_target_id, attach_target_type, local, body)


# --- deprecated ---


@router.get(
    "/galaxy_clusters/view/{galaxyClusterId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    summary="Gets information from a galaxy cluster",
)
@alog
async def get_galaxy_cluster_view(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    cluster_id: Annotated[int | UUID, Path(alias="galaxyClusterId")],
) -> GalaxyClusterResponse:
    """Deprecated
    Returns information from a galaxy cluster selected by its id.

    args:

    - the user's authentification status
    - the current database
    - the galaxy id

    returns:

    - the information of the galaxy cluster
    """
    return await _get_galaxy_cluster(db, await _load_galaxy_cluster(db, cluster_id))


@router.put(
    "/galaxy_clusters/edit/{galaxy_cluster_id}",
    status_code=status.HTTP_200_OK,
    summary="Update galaxy cluster",
)
async def put_galaxy_cluster(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_cluster_id: Annotated[int | UUID, Path(alias="galaxy_cluster_id")],
    body: PutGalaxyClusterRequest,
) -> GalaxyClusterResponse:
    if isinstance(galaxy_cluster_id, int):
        filter_rule = GalaxyCluster.id == galaxy_cluster_id
    else:
        filter_rule = GalaxyCluster.uuid == galaxy_cluster_id

    # get galaxy
    qry = select(GalaxyCluster).filter(filter_rule).options(selectinload(GalaxyCluster.galaxy_elements))

    result = await db.execute(qry)
    galaxy_cluster = result.scalar_one_or_none()

    if galaxy_cluster is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Galaxy Cluster not found")

    galaxy_cluster.patch(**body.model_dump(exclude_unset=True))
    if body.GalaxyElement is not None:
        await update_galaxy_cluster_elements(db, galaxy_cluster, body.GalaxyElement)
    await db.flush()
    db.expire(galaxy_cluster)
    return await _get_galaxy_cluster(db, await _load_galaxy_cluster(db, galaxy_cluster_id))


@router.post(
    "/galaxy_clusters/add/{galaxyId}",
    status_code=status.HTTP_200_OK,
    summary="Add new galaxy cluster",
)
@alog
async def add_galaxy_cluster(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[int | UUID, Path(alias="galaxyId")],
    body: AddGalaxyClusterRequest,
) -> GalaxyClusterResponse:
    if isinstance(galaxy_id, int):
        filter_rule = Galaxy.id == galaxy_id
    else:
        filter_rule = Galaxy.uuid == galaxy_id

    # get galaxy
    result = await db.execute(select(Galaxy).filter(filter_rule))
    galaxy = result.scalar_one_or_none()

    if galaxy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Galaxy not found")
    # get new uuid
    if body.uuid is None:
        body.uuid = uuid()

    tag_name = galaxy_tag_name(galaxy.type, body.uuid)

    new_galaxy_cluster = GalaxyCluster(
        uuid=body.uuid,
        value=body.value,
        description=body.description,
        source=body.source,
        galaxy_id=galaxy.id,
        distribution=body.distribution,
        authors=body.authors,
        tag_name=tag_name,
        type=galaxy.type,
        org_id=body.org_id if body.org_id else auth.org_id,
        orgc_id=body.orgc_id if body.orgc_id else auth.org_id,
        version=int(time.time()),
        locked=body.locked,
    )
    db.add(new_galaxy_cluster)
    await db.flush()

    for ge in body.GalaxyElement:
        new_galaxy_element = GalaxyElement(galaxy_cluster_id=new_galaxy_cluster.id, key=ge.key, value=ge.value)
        db.add(new_galaxy_element)
    await db.flush()

    return await _get_galaxy_cluster(db, await _load_galaxy_cluster(db, new_galaxy_cluster.id))


@router.get(
    "/galaxy_clusters/index/{galaxyId}",
    status_code=status.HTTP_200_OK,
    summary="Add new galaxy cluster",
)
@alog
async def index_galaxy_cluster_by_galaxy_id(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[int, Path(alias="galaxyId")],
) -> list[IndexGalaxyCluster]:
    # get galaxy
    query = select(Galaxy).filter(Galaxy.id == galaxy_id).options(selectinload(Galaxy.galaxy_clusters))
    result = await db.execute(query)
    galaxy = result.scalar_one_or_none()

    if galaxy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Galaxy not found")

    response = []
    galaxy_resp = ShortCommonGalaxy(**galaxy.asdict())
    for gc in galaxy.galaxy_clusters:
        response.append(IndexGalaxyCluster(Galaxy=galaxy_resp, GalaxyCluster=ShortCommonGalaxyCluster(**gc.asdict())))

    return response


@router.post(
    "/galaxy_clusters/restsearch",
    status_code=status.HTTP_200_OK,
    summary="Search galaxy_clusters",
)
async def restsearch(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: GalaxyClusterSearchBody,
) -> GalaxyClusterSearchResponse:
    # TODO not right implemented
    """Search for galaxy_clusters based on various filters.

    Input:

    - the user's authentification status

    - the current database

    - the request body

    Output:

    - the galaxy_clusters found by search
    """
    return await _restsearch(db, body)


# --- endpoint logic ---
async def _restsearch(db: Session, body: GalaxyClusterSearchBody) -> GalaxyClusterSearchResponse:
    minimal = body.minimal

    galaxy_clusters = await _load_galaxy_clusters_with_filters(db=db, filters=body)

    galaxy_clusters_response_list: list[SearchGalaxyClusterGalaxyClusters] = []
    if minimal:
        for galaxy_cluster in galaxy_clusters:
            galaxy_clusters_response_list.append(await _get_minimal_galaxy_cluster_search_response(db, galaxy_cluster))
    else:
        for galaxy_cluster in galaxy_clusters:
            galaxy_clusters_response_list.append(await _get_galaxy_cluster_search_response(db, galaxy_cluster))

    return GalaxyClusterSearchResponse(response=galaxy_clusters_response_list)


async def _load_galaxy_clusters_with_filters(db: Session, filters: GalaxyClusterSearchBody) -> Sequence[GalaxyCluster]:
    search_body: GalaxyClusterSearchBody = filters

    query = select(GalaxyCluster).options(
        joinedload(GalaxyCluster.galaxy),
        joinedload(GalaxyCluster.galaxy_elements),
        joinedload(GalaxyCluster.org),
    )

    if search_body.id:
        query = query.filter(GalaxyCluster.id.in_(search_body.id))

    if search_body.uuid:
        query = query.filter(GalaxyCluster.uuid.in_(search_body.uuid))

    if search_body.galaxy_id:
        query = query.filter(GalaxyCluster.galaxy_id == search_body.galaxy_id)

    if search_body.galaxy_uuid:
        query = query.filter(GalaxyCluster.galaxy.uuid)

    if search_body.published:
        query = query.filter(GalaxyCluster.published == search_body.published)

    if search_body.value:
        query = query.filter(GalaxyCluster.value == search_body.value)

    if search_body.extends_uuid:
        query = query.filter(GalaxyCluster.extends_uuid == search_body.extends_uuid)

    if search_body.extends_version:
        query = query.filter(GalaxyCluster.extends_version == search_body.extends_version)

    if search_body.version:
        query = query.filter(GalaxyCluster.version == search_body.version)

    if search_body.distribution:
        query = query.filter(GalaxyCluster.distribution == search_body.distribution)

    if search_body.org_id:
        query = query.filter(GalaxyCluster.org_id == search_body.org_id)

    if search_body.orgc_id:
        query = query.filter(GalaxyCluster.orgc_id == search_body.orgc_id)

    if search_body.tag_name:
        query = query.filter(GalaxyCluster.tag_name == search_body.tag_name)

    if search_body.custom:
        query = query.filter(GalaxyCluster.default != search_body.custom)

    if search_body.limit:
        query = query.limit(int(search_body.limit))

    result = await db.execute(query)
    return result.unique().scalars().all()


async def _get_minimal_galaxy_cluster_search_response(
    db: Session, galaxy_cluster: GalaxyCluster
) -> SearchGalaxyClusterGalaxyClusters:
    if galaxy_cluster.galaxy is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Galaxy not found")

    galaxy_dict: dict = (await _prepare_galaxy_response(db, galaxy_cluster.galaxy)).model_dump()
    galaxy_dict["created"] = str(galaxy_dict["created"])
    galaxy_dict["modified"] = str(galaxy_dict["modified"])

    parsed_cluster: SearchGalaxyClusterGalaxyClustersDetails = SearchGalaxyClusterGalaxyClustersDetails(
        uuid=galaxy_cluster.uuid,
        version=galaxy_cluster.version,
        Galaxy=RestSearchGalaxyBody(**galaxy_dict),
    )
    return SearchGalaxyClusterGalaxyClusters(GalaxyCluster=parsed_cluster)


async def _get_galaxy_cluster_search_response(
    db: Session, galaxy_cluster: GalaxyCluster
) -> SearchGalaxyClusterGalaxyClusters:
    if galaxy_cluster is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Galaxy cluster not found")

    galaxy_cluster_dict = galaxy_cluster.asdict()
    galaxy_cluster_dict = await _process_galaxy_cluster_dict(galaxy_cluster_dict)

    # Get the Galaxy
    galaxy = galaxy_cluster.galaxy

    if galaxy is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Galaxy not found")

    galaxy_cluster_dict["Galaxy"] = await _prepare_galaxy_response(db, galaxy)
    # Get the GalaxyElements
    galaxy_cluster_dict["GalaxyElement"] = [
        ExportGalaxyGalaxyElement(**ge.__dict__.copy()) for ge in galaxy_cluster.galaxy_elements
    ]

    # Get the Organisations
    org = galaxy_cluster.org if galaxy_cluster.org_id != 0 else GENERIC_MISP_ORGANISATION
    orgc = galaxy_cluster.orgc if galaxy_cluster.orgc_id != 0 else GENERIC_MISP_ORGANISATION

    galaxy_cluster_dict["Org"] = await _get_organisation_for_cluster(db, org)
    galaxy_cluster_dict["Orgc"] = await _get_organisation_for_cluster(db, orgc)

    return SearchGalaxyClusterGalaxyClusters(
        GalaxyCluster=SearchGalaxyClusterGalaxyClustersDetails(**galaxy_cluster_dict)
    )


async def _import_galaxy_cluster(
    db: Session, body: list[ImportGalaxyBody], request: Request
) -> DeleteForceUpdateImportGalaxyResponse:
    successfully_imported_counter = 0
    failed_imports_counter = 0

    for element in body:
        element_dict = element.model_dump()

        galaxy_cluster = element_dict["GalaxyCluster"]
        galaxy_cluster_dict = galaxy_cluster

        galaxy_elements = galaxy_cluster_dict["GalaxyElement"]

        galaxy_cluster_type = galaxy_cluster_dict["type"]

        result = await db.execute(select(Galaxy).filter(Galaxy.type == galaxy_cluster_type))
        galaxies_with_given_type = result.scalars().all()

        if galaxy_cluster_dict["default"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=DeleteForceUpdateImportGalaxyResponse(
                    saved=False,
                    name="Could not import Galaxy",
                    message="Could not import Galaxy",
                    url=str(request.url.path),
                    errors=f"Could not import galaxy clusters. {successfully_imported_counter} imported, 0 ignored,"
                    f"{failed_imports_counter} failed. Only non-default clusters can be saved",
                ).model_dump(),
            )
        elif len(galaxies_with_given_type) == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=DeleteForceUpdateImportGalaxyResponse(
                    saved=False,
                    name="Could not import Galaxy",
                    message="Could not import Galaxy",
                    url=str(request.url.path),
                    errors=f"Could not import galaxy clusters. {successfully_imported_counter} imported, 0 ignored,"
                    f"{failed_imports_counter} failed. Galaxy not found",
                ).model_dump(),
            )
        else:
            del galaxy_cluster_dict["GalaxyElement"]

            new_galaxy_cluster = GalaxyCluster(
                type=galaxy_cluster["type"],
                value=galaxy_cluster["value"],
                tag_name=galaxy_cluster["tag_name"],
                description=galaxy_cluster["description"],
                galaxy_id=galaxy_cluster["galaxy_id"],
                source=galaxy_cluster["source"],
                authors=galaxy_cluster["authors"],
                version=galaxy_cluster["version"],
                distribution=galaxy_cluster["distribution"],
                sharing_group_id=galaxy_cluster["sharing_group_id"],
                org_id=galaxy_cluster["org_id"],
                orgc_id=galaxy_cluster["orgc_id"],
                default=galaxy_cluster["default"],
                locked=galaxy_cluster["locked"],
                extends_uuid=galaxy_cluster["extends_uuid"],
                extends_version=galaxy_cluster["extends_version"],
                published=galaxy_cluster["published"],
                deleted=galaxy_cluster["deleted"],
            )

            db.add(new_galaxy_cluster)
            await db.flush()

            for galaxy_element in galaxy_elements:
                galaxy_element["galaxy_cluster_id"] = new_galaxy_cluster.id

                del galaxy_element["id"]

                new_galaxy_element = GalaxyElement(**{**galaxy_element})

                db.add(new_galaxy_element)
                await db.flush()

        successfully_imported_counter += 1

    if failed_imports_counter > 0:
        return DeleteForceUpdateImportGalaxyResponse(
            saved=False,
            name="Could not import Galaxy",
            message="Could not import Galaxy",
            url=str(request.url.path),
            errors=f"Could not import galaxy clusters. 0 imported, 0 ignored, {failed_imports_counter} failed.",
        )

    return DeleteForceUpdateImportGalaxyResponse(
        saved=True,
        success=True,
        name=f"Galaxy clusters imported. {successfully_imported_counter} imported, 0 ignored, 0 failed.",
        message=f"Galaxy clusters imported. {successfully_imported_counter} imported, 0 ignored, 0 failed.",
        url=str(request.url.path),
    )


@alog
async def _process_galaxy_cluster_dict(cluster_dict: dict) -> dict:
    if not isinstance(cluster_dict["authors"], list):
        cluster_dict["authors"] = parse_galaxy_authors(cluster_dict["authors"])

    if cluster_dict.get("collection_uuid") is None:
        cluster_dict["collection_uuid"] = ""
    if cluster_dict.get("distribution") is None:
        cluster_dict["distribution"] = "0"
    else:
        cluster_dict["distribution"] = str(cluster_dict["distribution"])

    bool_fields_to_convert = ["default", "locked", "published", "deleted"]
    for field in bool_fields_to_convert:
        if cluster_dict.get(field) is None:
            cluster_dict[field] = False

    return cluster_dict


async def _load_galaxy_cluster(db: Session, cluster_id: int | UUID) -> GalaxyCluster | None:
    if isinstance(cluster_id, int):
        filter_rule = GalaxyCluster.id == cluster_id
    else:
        filter_rule = GalaxyCluster.uuid == cluster_id

    result = await db.execute(
        select(GalaxyCluster)
        .filter(filter_rule)
        .options(
            selectinload(GalaxyCluster.org),
            selectinload(GalaxyCluster.orgc),
            selectinload(GalaxyCluster.galaxy),
            selectinload(GalaxyCluster.galaxy_elements),
        )
    )
    return result.scalar_one_or_none()


@alog
async def _get_galaxy_cluster(db: Session, galaxy_cluster: GalaxyCluster | None) -> GalaxyClusterResponse:
    if galaxy_cluster is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Galaxy cluster not found")

    galaxy_cluster_dict = galaxy_cluster.asdict()
    galaxy_cluster_dict = await _process_galaxy_cluster_dict(galaxy_cluster_dict)

    # Get the Galaxy
    galaxy = galaxy_cluster.galaxy

    if galaxy is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Galaxy not found")

    galaxy_cluster_dict["Galaxy"] = (await _prepare_galaxy_response(db, galaxy)).model_dump()
    # Get the GalaxyElements
    galaxy_cluster_dict["GalaxyElement"] = [
        ExportGalaxyGalaxyElement(**ge.asdict()).model_dump() for ge in galaxy_cluster.galaxy_elements
    ]

    # Get the Organisations
    org = galaxy_cluster.org if galaxy_cluster.org_id != 0 else GENERIC_MISP_ORGANISATION
    orgc = galaxy_cluster.orgc if galaxy_cluster.orgc_id != 0 else GENERIC_MISP_ORGANISATION

    galaxy_cluster_dict["Org"] = await _get_organisation_for_cluster(db, org)
    galaxy_cluster_dict["Orgc"] = await _get_organisation_for_cluster(db, orgc)

    return GalaxyClusterResponse(GalaxyCluster=GetGalaxyClusterResponse.model_validate(galaxy_cluster_dict))


@alog
async def _get_organisation_for_cluster(db: Session, org: Organisation) -> GetOrganisationElement:
    if org is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Organisation not found")

    return GetOrganisationElement(
        id=org.id,
        name=org.name,
        date_created=org.date_created,
        date_modified=org.date_modified,
        description=org.description,
        type=org.type,
        nationality=org.nationality,
        sector=org.sector,
        created_by=org.created_by,
        uuid=org.uuid,
        contacts=org.contacts,
        local=org.local,
        restricted_to_domain=org.restricted_to_domain,
        landingpage=org.landingpage,
    )


@alog
async def _export_galaxy(db: Session, galaxy_id: str, body: ExportGalaxyBody) -> list[ExportGalaxyClusterResponse]:
    galaxy: Galaxy | None = await db.get(Galaxy, galaxy_id)

    if not galaxy:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    body_dict = body.model_dump()

    missing_information_in_body = False

    if "Galaxy" not in body_dict:
        missing_information_in_body = True

    body_dict_information = body_dict["Galaxy"]

    if "default" not in body_dict_information:
        missing_information_in_body = True
    elif "distribution" not in body_dict_information:
        missing_information_in_body = True

    if missing_information_in_body:
        return []

    response_list = await _prepare_export_galaxy_response(db, galaxy_id, body_dict_information)

    return response_list


@alog
async def _attach_cluster_to_galaxy(
    db: Session,
    user: User,
    attach_target_id: str,
    attach_target_type: AttachTargetTypes,
    local: bool,
    body: AttachClusterGalaxyBody,
) -> AttachClusterGalaxyResponse:
    galaxy_cluster_id = body.Galaxy.target_id
    galaxy_cluster: GalaxyCluster | None = await db.get(GalaxyCluster, galaxy_cluster_id)

    if not galaxy_cluster:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid Galaxy cluster.")

    tag = await get_or_create_instance_tag(
        db, user, galaxy_cluster.tag_name, ignore_permissions=True, new_tag_local_only=False, is_galaxy_tag=True
    )
    tag_id = tag.id

    if attach_target_type == AttachTargetTypes.EVENT:
        event: Event | None = await db.get(Event, attach_target_id)

        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid event.")
        new_event_tag = EventTag(event_id=event.id, tag_id=tag_id, local=True if int(local) == 1 else False)
        db.add(new_event_tag)
        await db.flush()
    elif attach_target_type == AttachTargetTypes.ATTRIBUTE:
        attribute: Attribute | None = await db.get(Attribute, attach_target_id)

        if not attribute:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid attribute.")
        new_attribute_tag = AttributeTag(
            attribute_id=attribute.id,
            event_id=attribute.event_id,
            tag_id=tag_id,
            local=True if int(local) == 1 else False,
        )
        db.add(new_attribute_tag)
        await db.flush()
    elif attach_target_type == AttachTargetTypes.TAG_COLLECTION:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Attachment to tag_collection is not available yet."
        )

    return AttachClusterGalaxyResponse(saved=True, success="Cluster attached.", check_publish=True)


@alog
async def _prepare_galaxy_response(db: Session, galaxy: Galaxy) -> RestSearchGalaxyBody:
    galaxy_dict = galaxy.asdict()
    result = await db.execute(select(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id).limit(1))
    galaxy_cluster = result.scalars().first()

    if galaxy_cluster is None:
        galaxy_dict["local_only"] = True

    return RestSearchGalaxyBody(**galaxy_dict)


@alog
async def _prepare_galaxy_cluster_response(db: Session, galaxy: Galaxy) -> list[GalaxyClusterResponse]:
    result = await db.execute(
        select(GalaxyCluster)
        .filter(GalaxyCluster.galaxy_id == galaxy.id)
        .options(
            selectinload(GalaxyCluster.org),
            selectinload(GalaxyCluster.orgc),
            selectinload(GalaxyCluster.galaxy),
            selectinload(GalaxyCluster.galaxy_elements),
        )
    )
    galaxy_cluster_list = result.scalars().all()

    return [await _get_galaxy_cluster(db, gc) for gc in galaxy_cluster_list]


@alog
async def _prepare_export_galaxy_response(
    db: Session, galaxy_id: str, body_dict_information: dict
) -> list[ExportGalaxyClusterResponse]:
    response_list = []
    galaxy = await db.get(Galaxy, galaxy_id)
    if galaxy is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    galaxy_cluster_response_list = await _prepare_galaxy_cluster_response(db, galaxy)
    for galaxy_cluster_response in galaxy_cluster_response_list:
        galaxy_cluster = galaxy_cluster_response.GalaxyCluster
        if galaxy_cluster.distribution != body_dict_information["distribution"]:
            continue
        elif galaxy_cluster.default != body_dict_information["default"]:
            continue
        galaxy_cluster_dict = galaxy_cluster.model_dump()

        result = await db.execute(
            select(GalaxyReference).filter(GalaxyReference.galaxy_cluster_id == galaxy_cluster.id)
        )
        galaxy_cluster_relation_list = result.scalars().all()

        galaxy_cluster_dict["GalaxyClusterRelation"] = await _prepare_galaxy_cluster_relation_response(
            db, galaxy_cluster_relation_list
        )
        response_list.append(ExportGalaxyClusterResponse(**galaxy_cluster_dict))

    return response_list


@alog
async def _prepare_galaxy_cluster_relation_response(
    db: Session, galaxy_cluster_relation_list: Sequence[GalaxyReference]
) -> list[AddEditGetEventGalaxyClusterRelation]:
    galaxy_cluster_relation_response_list = []

    for galaxy_cluster_relation in galaxy_cluster_relation_list:
        galaxy_cluster_relation_dict = galaxy_cluster_relation.asdict()

        result = await db.execute(
            select(GalaxyCluster).filter(GalaxyCluster.id == galaxy_cluster_relation.galaxy_cluster_id).limit(1)
        )
        related_galaxy_cluster = result.scalars().one()

        result = await db.execute(select(Tag).filter(Tag.name == related_galaxy_cluster.tag_name))
        tag_list = result.scalars().all()

        if len(tag_list) > 0:
            galaxy_cluster_relation_dict["Tag"] = _prepare_tag_response(tag_list)

        galaxy_cluster_relation_galaxy_cluster = await db.get(GalaxyCluster, galaxy_cluster_relation.galaxy_cluster_id)

        if galaxy_cluster_relation_galaxy_cluster is None:
            continue

        galaxy_cluster_relation_dict["galaxy_cluster_uuid"] = galaxy_cluster_relation_galaxy_cluster.uuid
        galaxy_cluster_relation_dict["distribution"] = galaxy_cluster_relation_galaxy_cluster.distribution
        galaxy_cluster_relation_dict["default"] = galaxy_cluster_relation_galaxy_cluster.default
        galaxy_cluster_relation_dict["sharing_group_id"] = galaxy_cluster_relation_galaxy_cluster.sharing_group_id

        galaxy_cluster_relation_response_list.append(
            AddEditGetEventGalaxyClusterRelation(**galaxy_cluster_relation_dict)
        )

    return galaxy_cluster_relation_response_list


@log
def _prepare_tag_response(tag_list: Sequence[Any]) -> list[AddEditGetEventGalaxyClusterRelationTag]:
    tag_response_list = []

    for tag in tag_list:
        tag_dict = tag.asdict()
        tag_dict["org_id"] = tag.org_id if tag.org_id is not None else "0"
        tag_dict["user_id"] = tag.user_id if tag.user_id is not None else "0"
        tag_dict["numerical_value"] = int(tag.numerical_value) if tag.numerical_value is not None else 0
        tag_response_list.append(AddEditGetEventGalaxyClusterRelationTag(**tag_dict))

    return tag_response_list
