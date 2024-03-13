import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path
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
from mmisp.api_schemas.organisations.organisation import Organisation as OrganisationSchema
from mmisp.db.database import get_db, with_session_management
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.event import Event, EventTag
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement, GalaxyReference
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.tag import Tag
from mmisp.util.partial import partial

router = APIRouter(tags=["galaxies"])
logging.basicConfig(level=logging.INFO)

info_format = "%(asctime)s - %(message)s"
error_format = "%(asctime)s - %(filename)s:%(lineno)d - %(message)s"

info_handler = logging.StreamHandler()
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter(info_format))

error_handler = logging.StreamHandler()
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(error_format))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(info_handler)
logger.addHandler(error_handler)


@router.post(
    "/galaxies/import",
    status_code=status.HTTP_200_OK,
    response_model=partial(DeleteForceUpdateImportGalaxyResponse),
    summary="Add new galaxy cluster",
    description="Add a new galaxy cluster to an existing galaxy.",
)
@with_session_management
async def import_galaxy_cluster(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    body: list[ImportGalaxyBody],
    request: Request,
) -> dict:
    return await _import_galaxy_cluster(db, body, request)


@router.get("/galaxies/view/{galaxyId}", deprecated=True)
@router.get("/galaxies/{galaxyId}", status_code=status.HTTP_200_OK, response_model=partial(GetGalaxyResponse))
@with_session_management
async def get_galaxy_details(
    db: Annotated[Session, Depends(get_db)], galaxy_id: Annotated[str, Path(..., alias="galaxyId")]
) -> dict:
    return await _get_galaxy_details(db, galaxy_id)


@router.post(
    "/galaxies/update",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=partial(DeleteForceUpdateImportGalaxyResponse),
    summary="Update galaxies",
    description="Force the galaxies to update with the JSON definitions. NOT YET IMPLEMENTED!",
)
@with_session_management
async def update_galaxy(
    dauth: Annotated[Auth, Depends(authorize(AuthStrategy.WORKER_KEY, [Permission.SYNC]))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return DeleteForceUpdateImportGalaxyResponse()


@router.delete("/galaxies/delete/{galaxyId}", deprecated=True)
@router.delete(
    "/galaxies/{galaxyId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(DeleteForceUpdateImportGalaxyResponse),
)
@with_session_management
async def delete_galaxy(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[str, Path(..., alias="galaxyId")],
    request: Request,
) -> dict:
    return await _delete_galaxy(db, galaxy_id, request)


@router.get("/galaxies", status_code=status.HTTP_200_OK)
@with_session_management
async def get_galaxies(db: Annotated[Session, Depends(get_db)]) -> list[GetAllSearchGalaxiesResponse]:
    return await _get_galaxies(db)


@router.post("/galaxies", status_code=status.HTTP_200_OK)
@with_session_management
async def search_galaxies(db: Annotated[Session, Depends(get_db)]) -> list[GetAllSearchGalaxiesResponse]:
    return await _get_galaxies(db)


@router.post(
    "/galaxies/export/{galaxyId}",
    status_code=status.HTTP_200_OK
)
@with_session_management
async def export_galaxy(
    db: Annotated[Session, Depends(get_db)],
    galaxy_id: Annotated[str, Path(..., alias="galaxyId")],
    body: ExportGalaxyBody,
) -> list[ExportGalaxyClusterResponse]:
    return await _export_galaxy(db, galaxy_id, body)


@router.post(
    "/galaxies/attachCluster/{attachTargetId}/{attachTargetType}/local:{local}",
    status_code=status.HTTP_200_OK,
    response_model=partial(AttachClusterGalaxyResponse),
)
@with_session_management
async def galaxies_attachCluster(
    local: str,
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    attach_target_id: Annotated[str, Path(..., alias="attachTargetId")],
    attach_target_type: Annotated[str, Path(..., alias="attachTargetType")],
    body: AttachClusterGalaxyBody,
) -> dict:
    return await _attach_cluster_to_galaxy(db, attach_target_id, attach_target_type, local, body)


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

        galaxies_with_given_type = db.query(Galaxy).filter(Galaxy.type == galaxy_cluster_type).all()

        if galaxy_cluster_dict["default"] is True:
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
            db.commit()
            for galaxy_element in galaxy_elements:
                galaxy_element["galaxy_cluster_id"] = new_galaxy_cluster.id

                del galaxy_element["id"]

                new_galaxy_element = GalaxyElement(**{**galaxy_element})

                db.add(new_galaxy_element)
                db.commit()
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


async def _get_galaxy_details(db: Session, galaxy_id: str) -> dict:
    galaxy: Galaxy | None = db.get(Galaxy, galaxy_id)

    if not galaxy:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    galaxy_data = _prepare_galaxy_response(db, galaxy)
    galaxy_cluster_data = _prepare_galaxy_cluster_response(db, galaxy)

    return GetGalaxyResponse(Galaxy=galaxy_data, GalaxyCluster=galaxy_cluster_data)


async def _delete_galaxy(db: Session, galaxy_id: str, request: Request) -> DeleteForceUpdateImportGalaxyResponse:
    galaxy = db.get(Galaxy, galaxy_id)

    if not galaxy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DeleteForceUpdateImportGalaxyResponse(
                saved=False, success=False, name="Invalid galaxy.", message="Invalid galaxy.", url=str(request.url.path)
            ).dict(),
        )
    connected_tag_name = db.query(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id).first().tag_name
    connected_tag = db.query(Tag).filter(Tag.name == connected_tag_name).first()

    db.delete(galaxy)
    db.delete(connected_tag)
    db.commit()

    return DeleteForceUpdateImportGalaxyResponse(
        saved=True, success=True, name="Galaxy deleted", message="Galaxy deleted", url=str(request.url.path)
    )


async def _get_galaxies(db: Session) -> list[GetAllSearchGalaxiesResponse]:
    galaxies = db.query(Galaxy).all()
    response_list = []

    if not galaxies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No galaxies found.")

    for galaxy in galaxies:
        response_list.append(GetAllSearchGalaxiesResponse(Galaxy=_prepare_galaxy_response(db, galaxy)))

    return response_list


async def _export_galaxy(db: Session, galaxy_id: str, body: ExportGalaxyBody) -> list[dict]:
    galaxy: Galaxy | None = db.get(Galaxy, galaxy_id)

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

    if missing_information_in_body is True:
        return []

    response_list = _prepare_export_galaxy_response(db, galaxy_id, body_dict_information)

    return response_list


async def _attach_cluster_to_galaxy(
    db: Session, attach_target_id: str, attach_target_type: str, local: str, body: AttachClusterGalaxyBody
) -> AttachClusterGalaxyResponse:
    galaxy_cluster_id = body.Galaxy.target_id
    galaxy_cluster: GalaxyCluster | None = db.get(GalaxyCluster, galaxy_cluster_id)

    if not galaxy_cluster:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid Galaxy cluster.")

    if local not in ["0", "1"]:
        local = "0"

    tag_id = db.query(Tag).filter(Tag.name == galaxy_cluster.tag_name).first().id

    if attach_target_type == "event":
        event: Event | None = db.get(Event, attach_target_id)

        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid event.")
        new_event_tag = EventTag(event_id=event.id, tag_id=tag_id, local=True if int(local) == 1 else False)
        db.add(new_event_tag)
        db.commit()
    elif attach_target_type == "attribute":
        attribute: Attribute | None = db.get(Attribute, attach_target_id)

        if not attribute:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid attribute.")
        new_attribute_tag = AttributeTag(
            attribute_id=attribute.id,
            event_id=attribute.event_id,
            tag_id=tag_id,
            local=True if int(local) == 1 else False,
        )
        db.add(new_attribute_tag)
        db.commit()
    elif attach_target_type == "tag_collection":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Attachment to tag_collection is not available yet."
        )
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error occurred.")

    return AttachClusterGalaxyResponse(saved=True, success="Cluster attached.", check_publish=True)


def _prepare_galaxy_response(db: Session, galaxy: Galaxy) -> GetAllSearchGalaxiesAttributes:
    galaxy_dict = galaxy.__dict__.copy()
    galaxy_cluster = db.query(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id).first()

    if galaxy_cluster is None:
        galaxy_dict["local_only"] = True

    return GetAllSearchGalaxiesAttributes(**galaxy_dict)


def _prepare_galaxy_cluster_response(db: Session, galaxy: Galaxy) -> list[GetGalaxyClusterResponse]:
    response_list = []

    galaxy_cluster_list = db.query(GalaxyCluster).filter(GalaxyCluster.galaxy_id == galaxy.id).all()

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

            galaxy_element_list = (
                db.query(GalaxyElement).filter(GalaxyElement.galaxy_cluster_id == galaxy_cluster.id).all()
            )
            galaxy_cluster_dict["GalaxyElement"] = []

            if len(galaxy_element_list) > 0:
                for galaxy_element in galaxy_element_list:
                    galaxy_element_dict = galaxy_element.__dict__.copy()
                    galaxy_cluster_dict["GalaxyElement"].append(ExportGalaxyGalaxyElement(**galaxy_element_dict))

            response_list.append(GetGalaxyClusterResponse(**galaxy_cluster_dict))

    return response_list


def _prepare_export_galaxy_response(
    db: Session, galaxy_id: str, body_dict_information: dict
) -> list[ExportGalaxyClusterResponse]:
    response_list = []
    galaxy = db.get(Galaxy, galaxy_id)
    galaxy_response = _prepare_galaxy_response(db, galaxy)
    galaxy_cluster_response_list = _prepare_galaxy_cluster_response(db, galaxy)
    for galaxy_cluster in galaxy_cluster_response_list:
        if galaxy_cluster.distribution != body_dict_information["distribution"]:
            continue
        elif galaxy_cluster.default != body_dict_information["default"]:
            continue
        org = db.get(Organisation, galaxy_cluster.org_id)
        orgc = db.get(Organisation, galaxy_cluster.orgc_id)
        galaxy_cluster_dict = galaxy_cluster.dict()
        galaxy_cluster_dict["Org"] = OrganisationSchema(**org.__dict__.copy())
        galaxy_cluster_dict["Orgc"] = OrganisationSchema(**orgc.__dict__.copy())
        galaxy_cluster_dict["Galaxy"] = GetAllEventsGalaxyClusterGalaxy(**galaxy_response.__dict__.copy())
        galaxy_cluster_relation_list = (
            db.query(GalaxyReference).filter(GalaxyReference.galaxy_cluster_id == galaxy_cluster.id).all()
        )

        galaxy_cluster_dict["GalaxyClusterRelation"] = _prepare_galaxy_cluster_relation_response(
            db, galaxy_cluster_relation_list
        )
        response_list.append(ExportGalaxyClusterResponse(**galaxy_cluster_dict))

    return response_list


def _prepare_galaxy_cluster_relation_response(
    db: Session, galaxy_cluster_relation_list: list[GalaxyReference]
) -> list[AddEditGetEventGalaxyClusterRelation]:
    galaxy_cluster_relation_response_list = []

    for galaxy_cluster_relation in galaxy_cluster_relation_list:
        galaxy_cluster_relation_dict = galaxy_cluster_relation.__dict__.copy()
        related_galaxy_cluster = (
            db.query(GalaxyCluster).filter(GalaxyCluster.id == galaxy_cluster_relation.galaxy_cluster_id).first()
        )
        tag_list = db.query(Tag).filter(Tag.name == related_galaxy_cluster.tag_name).all()
        if len(tag_list) > 0:
            galaxy_cluster_relation_dict["Tag"] = _prepare_tag_response(tag_list)

        galaxy_cluster_relation_dict["galaxy_cluster_uuid"] = db.get(
            GalaxyCluster, galaxy_cluster_relation.galaxy_cluster_id
        ).uuid
        galaxy_cluster_relation_dict["distribution"] = db.get(
            GalaxyCluster, galaxy_cluster_relation.galaxy_cluster_id
        ).distribution
        galaxy_cluster_relation_dict["default"] = db.get(
            GalaxyCluster, galaxy_cluster_relation.galaxy_cluster_id
        ).default
        galaxy_cluster_relation_dict["sharing_group_id"] = db.get(
            GalaxyCluster, galaxy_cluster_relation.galaxy_cluster_id
        ).sharing_group_id

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
