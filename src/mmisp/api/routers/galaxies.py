from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.events.add_edit_get_event_response import (
    AddEditGetEventGalaxyClusterRelation,
    AddEditGetEventGalaxyClusterRelationTag,
)
from mmisp.api_schemas.events.get_all_events_response import GetAllEventsGalaxyClusterGalaxy
from mmisp.api_schemas.galaxies.attach_galaxy_cluster_body import AttachClusterGalaxyBody
from mmisp.api_schemas.galaxies.attach_galaxy_cluster_response import AttachClusterGalaxyResponse
from mmisp.api_schemas.galaxies.delete_force_update_import_galaxy_response import DeleteForceUpdateImportGalaxyResponse
from mmisp.api_schemas.galaxies.export_galaxies_body import ExportGalaxyBody
from mmisp.api_schemas.galaxies.export_galaxies_response import ExportGalaxyClusterResponse, ExportGalaxyGalaxyElement
from mmisp.api_schemas.galaxies.get_all_search_galaxies_response import (
    GetAllSearchGalaxiesAttributes,
    GetAllSearchGalaxiesResponse,
)
from mmisp.api_schemas.galaxies.get_galaxy_response import GetGalaxyClusterResponse, GetGalaxyResponse
from mmisp.api_schemas.galaxies.import_galaxies_body import ImportGalaxyBody
from mmisp.api_schemas.galaxies.search_galaxies_body import SearchGalaxiesbyValue
from mmisp.api_schemas.organisations.organisation import Organisation as OrganisationSchema
from mmisp.db.database import get_db, with_session_management
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.event import Event, EventTag
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement, GalaxyReference
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.tag import Tag

router = APIRouter(tags=["galaxies"])


@router.post(
    "/galaxies/import",
    status_code=status.HTTP_200_OK,
    response_model=DeleteForceUpdateImportGalaxyResponse,
    summary="Add new galaxy cluster",
    description="Add a new galaxy cluster to an existing galaxy.",
)
@with_session_management
async def import_galaxy_cluster(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.GALAXY_EDITOR]))],
    db: Annotated[Session, Depends(get_db)],
    body: list[ImportGalaxyBody],
    request: Request,
) -> DeleteForceUpdateImportGalaxyResponse:
    return await _import_galaxy_cluster(db, body, request)


@router.get("/galaxies/{galaxyId}", status_code=status.HTTP_200_OK, response_model=GetGalaxyResponse)
@with_session_management
async def get_galaxy_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[str, Path(alias="galaxyId")],
) -> GetGalaxyResponse:
    return await _get_galaxy_details(db, galaxy_id)


@router.post(
    "/galaxies/update",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=DeleteForceUpdateImportGalaxyResponse,
    summary="Update galaxies",
    description="Force the galaxies to update with the JSON definitions. NOT YET IMPLEMENTED!",
)
@with_session_management
async def update_galaxy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.WORKER_KEY, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> DeleteForceUpdateImportGalaxyResponse:
    return DeleteForceUpdateImportGalaxyResponse()


@router.delete(
    "/galaxies/{galaxyId}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteForceUpdateImportGalaxyResponse,
    summary="Delete a galaxy",
    description="Delete a specific galaxy by its Id.",
)
@with_session_management
async def delete_galaxy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[str, Path(alias="galaxyId")],
    request: Request,
) -> DeleteForceUpdateImportGalaxyResponse:
    return await _delete_galaxy(db, galaxy_id, request)


@router.get(
    "/galaxies",
    status_code=status.HTTP_200_OK,
    response_model=list[GetAllSearchGalaxiesResponse],
    summary="Get all galaxies",
    description="Get a list with all existing galaxies.",
)
@with_session_management
async def get_galaxies(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> list[GetAllSearchGalaxiesResponse]:
    return await _get_galaxies(db)


@router.post(
    "/galaxies",
    status_code=status.HTTP_200_OK,
    response_model=list[GetAllSearchGalaxiesResponse],
    summary="Search galaxies",
    description="Search galaxies by search term which matches with galaxy name, namespace, description, \
        kill_chain_order or uuid.",
)
@with_session_management
async def search_galaxies(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: SearchGalaxiesbyValue,
) -> list[GetAllSearchGalaxiesResponse]:
    return await _search_galaxies(db, body)


@router.post(
    "/galaxies/export/{galaxyId}",
    status_code=status.HTTP_200_OK,
    response_model=list[ExportGalaxyClusterResponse],
    summary="Export galaxy cluster",
    description="Export galaxy cluster.",
)
@with_session_management
async def export_galaxy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[str, Path(alias="galaxyId")],
    body: ExportGalaxyBody,
) -> list[ExportGalaxyClusterResponse]:
    return await _export_galaxy(db, galaxy_id, body)


@router.post(
    "/galaxies/attachCluster/{attachTargetId}/{attachTargetType}/local:{local}",
    status_code=status.HTTP_200_OK,
    response_model=AttachClusterGalaxyResponse,
    summary="Attach Cluster to Galaxy.",
    description="Attach a Galaxy Cluster to given Galaxy."
)
@with_session_management
async def galaxies_attachCluster(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    attach_target_id: Annotated[str, Path(alias="attachTargetId")],
    attach_target_type: Annotated[str, Path(alias="attachTargetType")],
    body: AttachClusterGalaxyBody,
    local: str,
) -> AttachClusterGalaxyResponse:
    return await _attach_cluster_to_galaxy(db, attach_target_id, attach_target_type, local, body)


# --- deprecated ---


@router.get(
    "/galaxies/view/{galaxyId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=GetGalaxyResponse,
    summary="View Galayx by ID.",
    description="View Galaxy by given Galaxy ID."
)
@with_session_management
async def get_galaxy_details_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[str, Path(alias="galaxyId")],
) -> GetGalaxyResponse:
    return await _get_galaxy_details(db, galaxy_id)


@router.delete(
    "/galaxies/delete/{galaxyId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=DeleteForceUpdateImportGalaxyResponse,
    summary="Delete Galaxy by ID",
    description="Delete Galaxy by GalaxyID."
)
@with_session_management
async def delete_galaxy_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[str, Path(alias="galaxyId")],
    request: Request,
) -> DeleteForceUpdateImportGalaxyResponse:
    return await _delete_galaxy(db, galaxy_id, request)


# --- endpoint logic ---


async def _import_galaxy_cluster(
    db: Session, body: list[ImportGalaxyBody], request: Request
) -> DeleteForceUpdateImportGalaxyResponse:
    successfully_imported_counter = 0
    failed_imports_counter = 0

    for element in body:
        element_dict = element.__dict__.copy()

        galaxy_cluster = element_dict["GalaxyCluster"]
        galaxy_cluster_dict = galaxy_cluster.dict()

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
                ).dict(),
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
                ).dict(),
            )
        else:
            galaxy_cluster_dict["authors"] = " ".join(galaxy_cluster_dict["authors"])
            del galaxy_cluster_dict["GalaxyElement"]

            new_galaxy_cluster = GalaxyCluster(
                type=galaxy_cluster.type,
                value=galaxy_cluster.value,
                tag_name=galaxy_cluster.tag_name,
                description=galaxy_cluster.description,
                galaxy_id=galaxy_cluster.galaxy_id,
                source=galaxy_cluster.source,
                authors=" ".join(galaxy_cluster.authors),
                version=galaxy_cluster.version,
                distribution=galaxy_cluster.distribution,
                sharing_group_id=galaxy_cluster.sharing_group_id,
                org_id=galaxy_cluster.org_id,
                orgc_id=galaxy_cluster.orgc_id,
                default=galaxy_cluster.default,
                locked=galaxy_cluster.locked,
                extends_uuid=galaxy_cluster.extends_uuid,
                extends_version=galaxy_cluster.extends_version,
                published=galaxy_cluster.published,
                deleted=galaxy_cluster.deleted,
            )

            db.add(new_galaxy_cluster)
            await db.commit()

            for galaxy_element in galaxy_elements:
                galaxy_element["galaxy_cluster_id"] = new_galaxy_cluster.id

                del galaxy_element["id"]

                new_galaxy_element = GalaxyElement(**{**galaxy_element})

                db.add(new_galaxy_element)
                await db.commit()

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


async def _get_galaxy_details(db: Session, galaxy_id: str) -> GetGalaxyResponse:
    galaxy: Galaxy | None = await db.get(Galaxy, galaxy_id)

    if not galaxy:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    galaxy_data = await _prepare_galaxy_response(db, galaxy)
    galaxy_cluster_data = await _prepare_galaxy_cluster_response(db, galaxy)

    return GetGalaxyResponse(Galaxy=galaxy_data, GalaxyCluster=galaxy_cluster_data)


async def _delete_galaxy(db: Session, galaxy_id: str, request: Request) -> DeleteForceUpdateImportGalaxyResponse:
    galaxy = await db.get(Galaxy, galaxy_id)

    if not galaxy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DeleteForceUpdateImportGalaxyResponse(
                saved=False, success=False, name="Invalid galaxy.", message="Invalid galaxy.", url=str(request.url.path)
            ).dict(),
        )

    result = await db.execute(select(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id).limit(1))
    connected_tag_name = result.scalars().first().tag_name

    result = await db.execute(select(Tag).filter(Tag.name == connected_tag_name))
    connected_tag = result.scalars().first()

    await db.delete(galaxy)
    await db.delete(connected_tag)
    await db.commit()

    return DeleteForceUpdateImportGalaxyResponse(
        saved=True, success=True, name="Galaxy deleted", message="Galaxy deleted", url=str(request.url.path)
    )


async def _get_galaxies(db: Session) -> list[GetAllSearchGalaxiesResponse]:
    result = await db.execute(select(Galaxy))
    galaxies = result.scalars().all()
    response_list = []

    if not galaxies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No galaxies found.")

    for galaxy in galaxies:
        response_list.append(GetAllSearchGalaxiesResponse(Galaxy=await _prepare_galaxy_response(db, galaxy)))

    return response_list


async def _search_galaxies(db: Session, body: SearchGalaxiesbyValue) -> list[GetAllSearchGalaxiesResponse]:
    search_term = body.value
    result = await db.execute(
        select(Galaxy).filter(
            Galaxy.name.contains(search_term),
            Galaxy.namespace.contains(search_term),
            Galaxy.description.contains(search_term),
            Galaxy.kill_chain_order.contains(search_term),
            Galaxy.uuid.contains(search_term),
        )
    )
    galaxies: list[Galaxy] = result.scalars().all()

    response_list = []

    for galaxy in galaxies:
        galaxy_dict = galaxy.__dict__
        response_list.append(GetAllSearchGalaxiesResponse(Galaxy=GetAllSearchGalaxiesAttributes(**galaxy_dict)))

    return response_list


async def _export_galaxy(db: Session, galaxy_id: str, body: ExportGalaxyBody) -> list[ExportGalaxyClusterResponse]:
    galaxy: Galaxy | None = await db.get(Galaxy, galaxy_id)

    if not galaxy:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    body_dict = body.dict()

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


async def _attach_cluster_to_galaxy(
    db: Session, attach_target_id: str, attach_target_type: str, local: str, body: AttachClusterGalaxyBody
) -> AttachClusterGalaxyResponse:
    galaxy_cluster_id = body.Galaxy.target_id
    galaxy_cluster: GalaxyCluster | None = await db.get(GalaxyCluster, galaxy_cluster_id)

    if not galaxy_cluster:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid Galaxy cluster.")

    if local not in ["0", "1"]:
        local = "0"

    result = await db.execute(select(Tag).filter(Tag.name == galaxy_cluster.tag_name).limit(1))
    tag_id = result.scalars().first().id

    if attach_target_type == "event":
        event: Event | None = await db.get(Event, attach_target_id)

        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid event.")
        new_event_tag = EventTag(event_id=event.id, tag_id=tag_id, local=True if int(local) == 1 else False)
        db.add(new_event_tag)
        await db.commit()
    elif attach_target_type == "attribute":
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
        await db.commit()
    elif attach_target_type == "tag_collection":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Attachment to tag_collection is not available yet."
        )
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error occurred.")

    return AttachClusterGalaxyResponse(saved=True, success="Cluster attached.", check_publish=True)


async def _prepare_galaxy_response(db: Session, galaxy: Galaxy) -> GetAllSearchGalaxiesAttributes:
    galaxy_dict = galaxy.__dict__.copy()

    result = await db.execute(select(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id).limit(1))
    galaxy_cluster = result.scalars().first()

    if galaxy_cluster is None:
        galaxy_dict["local_only"] = True

    return GetAllSearchGalaxiesAttributes(**galaxy_dict)


async def _prepare_galaxy_cluster_response(db: Session, galaxy: Galaxy) -> list[GetGalaxyClusterResponse]:
    response_list = []

    result = await db.execute(select(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id))
    galaxy_cluster_list = result.scalars().all()

    if len(galaxy_cluster_list) > 0:
        for galaxy_cluster in galaxy_cluster_list:
            galaxy_cluster_dict = galaxy_cluster.__dict__.copy()

            galaxy_cluster_dict["authors"] = galaxy_cluster_dict["authors"].split(" ")

            int_fields_to_convert = ["sharing_group_id", "org_id", "orgc_id", "extends_version"]
            for field in int_fields_to_convert:
                if galaxy_cluster_dict.get(field) is not None:
                    galaxy_cluster_dict[field] = str(galaxy_cluster_dict[field])
                else:
                    galaxy_cluster_dict[field] = "0"

            if galaxy_cluster_dict.get("collection_uuid") is None:
                galaxy_cluster_dict["collection_uuid"] = ""
            if galaxy_cluster_dict.get("extends_uuid") is None:
                galaxy_cluster_dict["extends_uuid"] = ""
            if galaxy_cluster_dict.get("distribution") is None:
                galaxy_cluster_dict["distribution"] = "0"
            else:
                galaxy_cluster_dict["distribution"] = str(galaxy_cluster_dict["distribution"])

            bool_fields_to_convert = ["default", "locked", "published", "deleted"]
            for field in bool_fields_to_convert:
                if galaxy_cluster_dict.get(field) is None:
                    galaxy_cluster_dict[field] = False

            result = await db.execute(
                select(GalaxyElement).filter(GalaxyElement.galaxy_cluster_id == galaxy_cluster.id)
            )
            galaxy_element_list = result.scalars().all()
            galaxy_cluster_dict["GalaxyElement"] = []

            if len(galaxy_element_list) > 0:
                for galaxy_element in galaxy_element_list:
                    galaxy_element_dict = galaxy_element.__dict__.copy()
                    galaxy_cluster_dict["GalaxyElement"].append(ExportGalaxyGalaxyElement(**galaxy_element_dict))

            response_list.append(GetGalaxyClusterResponse(**galaxy_cluster_dict))

    return response_list


async def _prepare_export_galaxy_response(
    db: Session, galaxy_id: str, body_dict_information: dict
) -> list[ExportGalaxyClusterResponse]:
    response_list = []
    galaxy = await db.get(Galaxy, galaxy_id)
    galaxy_response = await _prepare_galaxy_response(db, galaxy)
    galaxy_cluster_response_list = await _prepare_galaxy_cluster_response(db, galaxy)
    for galaxy_cluster in galaxy_cluster_response_list:
        if galaxy_cluster.distribution != body_dict_information["distribution"]:
            continue
        elif galaxy_cluster.default != body_dict_information["default"]:
            continue
        org = await db.get(Organisation, galaxy_cluster.org_id)
        orgc = await db.get(Organisation, galaxy_cluster.orgc_id)
        galaxy_cluster_dict = galaxy_cluster.dict()
        galaxy_cluster_dict["Org"] = OrganisationSchema(**org.__dict__.copy())
        galaxy_cluster_dict["Orgc"] = OrganisationSchema(**orgc.__dict__.copy())
        galaxy_cluster_dict["Galaxy"] = GetAllEventsGalaxyClusterGalaxy(**galaxy_response.__dict__.copy())

        result = await db.execute(
            select(GalaxyReference).filter(GalaxyReference.galaxy_cluster_id == galaxy_cluster.id)
        )
        galaxy_cluster_relation_list = result.scalars().all()

        galaxy_cluster_dict["GalaxyClusterRelation"] = await _prepare_galaxy_cluster_relation_response(
            db, galaxy_cluster_relation_list
        )
        response_list.append(ExportGalaxyClusterResponse(**galaxy_cluster_dict))

    return response_list


async def _prepare_galaxy_cluster_relation_response(
    db: Session, galaxy_cluster_relation_list: list[GalaxyReference]
) -> list[AddEditGetEventGalaxyClusterRelation]:
    galaxy_cluster_relation_response_list = []

    for galaxy_cluster_relation in galaxy_cluster_relation_list:
        galaxy_cluster_relation_dict = galaxy_cluster_relation.__dict__.copy()

        result = await db.execute(
            select(GalaxyCluster).filter(GalaxyCluster.id == galaxy_cluster_relation.galaxy_cluster_id).limit(1)
        )
        related_galaxy_cluster = result.scalars().first()

        result = await db.execute(select(Tag).filter(Tag.name == related_galaxy_cluster.tag_name))
        tag_list = result.scalars().all()

        if len(tag_list) > 0:
            galaxy_cluster_relation_dict["Tag"] = _prepare_tag_response(tag_list)

        galaxy_cluster_relation_galaxy_cluster = await db.get(GalaxyCluster, galaxy_cluster_relation.galaxy_cluster_id)

        galaxy_cluster_relation_dict["galaxy_cluster_uuid"] = galaxy_cluster_relation_galaxy_cluster.uuid
        galaxy_cluster_relation_dict["distribution"] = galaxy_cluster_relation_galaxy_cluster.distribution
        galaxy_cluster_relation_dict["default"] = galaxy_cluster_relation_galaxy_cluster.default
        galaxy_cluster_relation_dict["sharing_group_id"] = galaxy_cluster_relation_galaxy_cluster.sharing_group_id

        galaxy_cluster_relation_response_list.append(
            AddEditGetEventGalaxyClusterRelation(**galaxy_cluster_relation_dict)
        )

    return galaxy_cluster_relation_response_list


def _prepare_tag_response(tag_list: list[Any]) -> list[AddEditGetEventGalaxyClusterRelationTag]:
    tag_response_list = []

    for tag in tag_list:
        tag_dict = tag.__dict__.copy()
        tag_dict["org_id"] = tag.org_id if tag.org_id is not None else "0"
        tag_dict["user_id"] = tag.user_id if tag.user_id is not None else "0"
        tag_response_list.append(AddEditGetEventGalaxyClusterRelationTag(**tag_dict))

    return tag_response_list
